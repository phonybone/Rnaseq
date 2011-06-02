"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/compile.py $
$Id: compile.py 31209 2008-10-13 12:49:03Z dbinger $
"""
from copy import deepcopy
from os import stat, listdir
from os.path import join, splitext
from parser import compilest, sequence2st
from qpy.translate import statement_tree, expr_tree, get_power
from qpy.translate import translate_tokens, get_parse_tree
import py_compile
import symbol
import sys
import sys
import token

if sys.version < "3":
    import __builtin__ as builtins
else:
    import builtins

def get_argument(power):
    assert power[0] == symbol.power
    argument = power[2][2][1]
    assert argument[0] == symbol.argument
    return argument

def is_future_import_statement(node):
    try:
        return (node[0] == symbol.stmt and
            node[1][1][1][1][0] == symbol.import_from and
            node[1][1][1][1][2][1][1] == '__future__')
    except IndexError:
        return False

def is_atom_string(node):
    try:
        power = get_power(node)
        return (len(power) == 2 and
            power[1][0] == symbol.atom and
            power[1][1][0] == token.STRING)
    except IndexError:
        return False

def get_funcdef_function_name_child(node):
    assert node[0] == symbol.funcdef
    for child in node[1:]:
        if child[0] == 1 and child[1] != 'def':
            return child

class Transform (object):

    def __init__(self, tree):
        self.tree = tree
        self.template_type_stack = [None]
        self.module_start = statement_tree(
            'from qpy.quoted import join_xml as _qpy_join_xml, '
            'join_str as _qpy_join_str, xml as _qpy_xml')
        self.template_start = statement_tree(
            'qpy_accumulation=[];qpy_append=qpy_accumulation.append')
        self.return_xml = statement_tree(
            'return _qpy_join_xml(qpy_accumulation)')
        self.return_str = statement_tree(
            'return _qpy_join_str(qpy_accumulation)')
        self.qpy_append_expr_stmt = statement_tree('qpy_append(X)')[1][1][1]
        assert self.qpy_append_expr_stmt[0] == symbol.expr_stmt
        self.xml_power = get_power(expr_tree('_qpy_xml("X")'))
        self.template_type_stack = [None]
        self.traverse_node(self.tree)
        self.line_number = 1
        self.rationalize_line_numbers(self.tree)

    def rationalize_line_numbers(self, node):
        if not isinstance(node, list):
            return
        if len(node) == 3 and node[0] in token.tok_name:
            if node[2] < self.line_number:
                node[2] = self.line_number
            else:
                self.line_number = node[2]
        else:
            for child in node[1:]:
                self.rationalize_line_numbers(child)

    def traverse_node(self, node):
        if not isinstance(node, list):
            return
        # If this is a funcdef, push 'xml', 'str', or None
        if node[0] == symbol.funcdef:
            function_name = get_funcdef_function_name_child(node)[1]
            if function_name.endswith('__xml_template__'):
                self.template_type_stack.append('xml')
            elif function_name.endswith('__str_template__'):
                self.template_type_stack.append('str')
            else:
                self.template_type_stack.append(None)
        # Traverse down before doing modifications.
        for child in node[1:]:
            self.traverse_node(child)
        # Modify the node as necessary.
        if node[0] == symbol.file_input:
            # Insert module-level import statement.
            # Skip over the module docstring and any __future__ imports.
            for index, child in enumerate(node):
                if index == 0:
                    continue
                if is_atom_string(child):
                    continue
                if is_future_import_statement(child):
                    continue
                node.insert(index, deepcopy(self.module_start))
                break
        elif self.template_type_stack[-1] is None:
            pass # We're not in a template, so we're done.
        elif node[0] == symbol.expr_stmt and len(node) == 2:
            # Wrap this expression statement in a qpy_append call.
            stmt = deepcopy(self.qpy_append_expr_stmt)
            argument = get_argument(get_power(stmt))
            assert argument[1][0] == node[1][1][0]
            argument[1] = node[1][1]
            assert node[1][0] == stmt[1][0]
            node[1] = stmt[1]
        elif node[0] == symbol.funcdef:
            # This is a new template.
            # Insert the initialization of qpy_accumulation and qpy_append.
            func_suite = node[-1]
            for j, child in enumerate(func_suite[1:]):
                if child[0] == symbol.stmt:
                    func_suite.insert(j+1, deepcopy(self.template_start))
                    break
            # Add the appropriate return statement and patch function name.
            function_name_node = get_funcdef_function_name_child(node)
            function_name = function_name_node[1]
            if self.template_type_stack[-1] == 'xml':
                return_accumulation = deepcopy(self.return_xml)
                # trim __xml_template__
                function_name_node[1] = function_name_node[1][:-16] 
            else:
                assert self.template_type_stack[-1] == 'str'
                return_accumulation = deepcopy(self.return_str)
                # trim __str_template__                
                function_name_node[1] = function_name_node[1][:-16] 
            func_suite.insert(-1, return_accumulation)
        elif (self.template_type_stack[-1] == 'xml' and
            node[0] == symbol.power and
            node[1][0] == symbol.atom and
            node[1][1][0] == token.STRING):
            # node looks like
            # [power [atom [STRING "Z" 1]] ...]
            xml_power = deepcopy(self.xml_power)
            # xml_power looks like
            # [power
            #     [atom [STRING "_qpy_xml" 1]
            #     [trailer 
            #         LPAR ... 
            #         [arglist ... [power [atom [STRING "X"]]]]
            #         RPAR]]]
            argument = get_argument(xml_power)
            argument_power = get_power(argument)
            assert argument_power[1][0] == symbol.atom
            assert argument_power[1][0] == node[1][0]
            argument_power[1] = deepcopy(node[1]) # replace "X"
            node[1] = xml_power[1]
            node.insert(2, xml_power[2])
        # Pop the stack.
        if node[0] == symbol.funcdef:
            self.template_type_stack.pop()

    def get_st(self):
        return sequence2st(self.tree)

def get_code(source, source_name):
    translated_source = translate_tokens(source)
    tree = get_parse_tree(translated_source, source_name)
    transformed = Transform(tree).get_st()
    code = compilest(transformed, filename=source_name)
    return code

def timestamp(filename):
    try:
        s = stat(filename)
    except OSError:
        return None
    return s.st_mtime

def compile_qpy_file(source_name):
    """(source_name:str)
    Compile the given filename if it is a .qpy file and if it does not already
    have an up-to-date .pyc file.
    """
    if source_name[-4:] == '.qpy':
        compile_time = timestamp(source_name[:-4] + '.pyc')
        if compile_time is not None:
            source_time = timestamp(source_name)
            if compile_time >= source_time:
                return # already up-to-date
        compile(source_name)

def compile_qpy_files(path):
    """(path:str)
    Compile the .qpy files in the given directory.
    """
    for name in listdir(path):
        if name[-4:] == '.qpy':
            compile_qpy_file(join(path, name))

def compile(source_name):
    # Replace builtins.compile (temporarily) and use the py_compile module
    # to create the .pyc file using our special compile() function.
    output_name = splitext(source_name)[0] + ".pyc"
    builtins_compile = builtins.compile
    try:
        def qpycompile(source, source_name, extra='exec'):
            assert extra == 'exec'
            return get_code(source, source_name)
        builtins.compile = qpycompile
        py_compile.compile(source_name, cfile=output_name, doraise=True)
    finally:
        builtins.compile = builtins_compile

if __name__ == '__main__':
    import qpy.__main__
