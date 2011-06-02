#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/qpcheck.py $
$Id: qpcheck.py 31746 2009-07-21 13:03:12Z dbinger $
"""
from qpy.translate import get_parse_tree, symtree, translate_tokens
import symbol
import token
import sys
import keyword

python2 = not sys.version.startswith("3")

if python2:
    import __builtin__ as builtins
else:
    import builtins

def p(*args):
    for arg in args[:-1]:
        sys.stdout.write(str(arg) + " ")
    sys.stdout.write(str(args[-1]) + "\n")


class Namespace (object):

    def __init__(self, name, previous):
        self.names = set()
        self.name = name
        self.previous = previous

    def add(self, name):
        self.names.add(name)

    def update(self, names):
        for name in names:
            self.add(name)

    def __contains__(self, name):
        return name in self.names or name in self.previous

    def __str__(self):
        if not self.previous or not self.previous.get_previous():
            return self.name
        else:
            return str(self.previous) + "." + self.name

    def get_names(self):
        return self.names

    def get_base(self):
        if self.previous == []:
            return self
        else:
            return self.previous.get_base()

    def get_previous(self):
        return self.previous

def get_tree(filename):
    source = open(filename).read()
    if filename.endswith('.qpy'):
        source = translate_tokens(source)
    return get_parse_tree(source, filename)

def get_global_namespace():
    namespace = Namespace('GLOBAL', [])
    namespace.update(keyword.kwlist)
    namespace.add('__builtins__')
    namespace.add('__doc__')
    namespace.add('__file__')
    namespace.add('__name__')
    namespace.add('__path__')
    namespace.update(dir(builtins))
    return namespace

def get_node_name(node):
    number = node[0]
    return symbol.sym_name.get(number) or token.tok_name.get(number)

def get_name(node):
    if node[0] == token.NAME:
        return node[1]
    else:
        return None


def get_arglist_names(node):
    names = []
    node_name = get_node_name(node)
    if node_name not in ('typedargslist', 'varargslist'):
        return names
    if python2:
        defnames = ('fpdef', 'fplist')
    else:
        defnames =('tfpdef', 'vfpdef')
    todo = node[1:]
    while todo:
        child = todo[0]
        todo = todo[1:]
        if get_node_name(child) in defnames:
            todo += child[1:]
        if get_node_name(child) == 'NAME':
            name = get_name(child)
            names.append(name)
    return names

def gen_power(node):
    if isinstance(node, list):
        if node[0] == symbol.power:
            yield node
        for n in node[1:]:
            for p in gen_power(n):
                yield p

def gen_names(exprlist):
    # factor: ('+'|'-'|'~') factor | power
    # power: atom trailer* ['**' factor]
    # atom: ('(' [yield_expr|testlist_comp] ')' |
    #        '[' [testlist_comp] ']' |
    #        '{' [dictorsetmaker] '}' |
    #        NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')
    # testlist_comp: test ( comp_for | (',' test)* [','] )
    # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    for power in gen_power(exprlist):
        if len(power) == 2: # Just an atom
            atom = power[1]
            if atom[1][0] == token.NAME:
                yield get_name(atom[1])


def traverse(node, namespace, unresolved, unused):
    if not isinstance(node, list):
        return
    node_name = get_node_name(node)
    children  = node[1:]
    num_children = len(children)

    if node_name == 'NAME':
        name = get_name(node)
        if name not in namespace and '*' not in namespace:
            line_number = node[-1]
            unresolved[name] = (line_number, name, namespace)
        else:
            unused.discard(name)
        return

    if node_name == 'trailer' and children[0][0] == token.DOT:
        return

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # eval_input: testlist NEWLINE* ENDMARKER
    # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    # decorators: decorator+
    # decorated: decorators (classdef | funcdef)
    # funcdef: 'def' NAME parameters ['->' test] ':' suite
    if node_name == 'funcdef':
        if python2:
            name = get_name(children[-4])
            parameters = children[-3]
        else:
            name = get_name(children[1])
            parameters = children[2]

        if name.endswith('__xml_template__'):
            name = name[:-16]
        if name.endswith('__str_template__'):
            name = name[:-16]

        suite = children[-1]
        if get_node_name(children[-3]) != 'parameters':
            result_test = children[4]
            traverse(result_test, namespace, unresolved, unused)
        namespace = Namespace(name, namespace)
        traverse(parameters, namespace, unresolved, unused)
        namespace.get_previous().add(name)
        arg_names = get_arglist_names(parameters[-2])
        namespace.update(arg_names)
        traverse(suite, namespace, unresolved, unused)
        namespace = namespace.get_previous()
        return

    # parameters: '(' [typedargslist] ')'
    # typedargslist: ((tfpdef ['=' test] ',')*
    #                 ('*' [tfpdef] (',' tfpdef ['=' test])* [',' '**' tfpdef] | '**' tfpdef)
    #                 | tfpdef ['=' test] (',' tfpdef ['=' test])* [','])

    # tfpdef: NAME [':' test]
    if node_name == 'tfpdef':
        # Don't worry about resolving the parameter name.
        for child in children[1:]:
            traverse(child, namespace, unresolved, unused)
        return

    # varargslist: ((vfpdef ['=' test] ',')*
    #               ('*' [vfpdef] (',' vfpdef ['=' test])*  [',' '**' vfpdef] | '**' vfpdef)
    #               | vfpdef ['=' test] (',' vfpdef ['=' test])* [','])

    if node_name == 'varargslist':
        for j in range(1, len(children)):
            if get_node_name(children[j-1]) in ('STAR', 'DOUBLESTAR'):
                name = get_name(children[j])
                if name:
                    namespace.add(name)

    # vfpdef: NAME
    if node_name == 'vfpdef':
        # Don't worry about resolving the parameter name.
        return

    if python2 and node_name == 'fpdef':
        # Don't worry about resolving the parameter name.
        return

    # stmt: simple_stmt | compound_stmt
    # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
    # small_stmt: (expr_stmt | del_stmt | pass_stmt | flow_stmt |
    #              import_stmt | global_stmt | nonlocal_stmt | assert_stmt)

    # expr_stmt: testlist (augassign (yield_expr|testlist) |
    #                      ('=' (yield_expr|testlist))*)
    # You can't really assign to a yield expr.
    # The testlists must also be some kind of names.
    if node_name == 'expr_stmt':
        if num_children >= 3 and children[1][0] == token.EQUAL:
            traverse(node[-1], namespace, unresolved, unused)
            for child in children[:-2:2]:
                if child[0] == symbol.testlist:
                    names = list(gen_names(child))
                    namespace.update(names)
                else:
                    assert 0, symtree(node)

    # augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
    #             '<<=' | '>>=' | '**=' | '//=')
    # # For normal assignments, additional restrictions enforced by the interpreter
    # del_stmt: 'del' exprlist

    # pass_stmt: 'pass'
    # flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
    # break_stmt: 'break'
    # continue_stmt: 'continue'
    # return_stmt: 'return' [testlist]
    # yield_stmt: yield_expr
    # raise_stmt: 'raise' [test ['from' test]]
    # import_stmt: import_name | import_from
    # import_name: 'import' dotted_as_names

    # # note below: the ('.' | '...') is necessary because '...' is tokenized as ELLIPSIS
    # import_from: ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
    #               'import' ('*' | '(' import_as_names ')' | import_as_names))

    if node_name == 'import_from':
        last_child = children[-1]
        if last_child[0] == token.STAR:
            namespace.add('*')
        else:
            if last_child[0] == symbol.import_as_names:
                import_as_names = last_child
            else:
                import_as_names = children[-2]
            assert import_as_names[0] == symbol.import_as_names
            for import_as_name in import_as_names[1::2]: # skip commas
                name = get_name(import_as_name[-1])
                namespace.add(name)
                unused.add(name)
        return

    # import_as_name: NAME ['as' NAME]
    if node_name == 'import_as_name':
        name = get_name(children[-1])
        namespace.add(name)
        return

    # dotted_as_name: dotted_name ['as' NAME]
    if node_name == 'dotted_as_name':
        if num_children == 1:
            dotted_name = children[0]
            names = []
            for n in dotted_name[1::2]:
                names.append(get_name(n))
                namespace.add('.'.join(names))
        else:
            name = get_name(children[-1])
            namespace.add(name)
        return

    # import_as_names: import_as_name (',' import_as_name)* [',']
    # dotted_as_names: dotted_as_name (',' dotted_as_name)*
    # dotted_name: NAME ('.' NAME)*
    if node_name == 'dotted_name':
        name = '.'.join(get_name(n) for n in node[1::2])
        return

    # global_stmt: 'global' NAME (',' NAME)*
    # nonlocal_stmt: 'nonlocal' NAME (',' NAME)*
    # assert_stmt: 'assert' test [',' test]
    #
    # compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
    # if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
    # while_stmt: 'while' test ':' suite ['else' ':' suite]

    # for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
    if node_name == 'for_stmt':
        exprlist = children[1]
        names = list(gen_names(exprlist))
        namespace.update(names)

    # try_stmt: ('try' ':' suite
    #            ((except_clause ':' suite)+
    #       ['else' ':' suite]
    #       ['finally' ':' suite] |
    #      'finally' ':' suite))
    # with_stmt: 'with' test [ with_var ] ':' suite

    # with_var: 'as' expr # python2.6
    # with_item: 'as' expr # python3.2

    if node_name in ('with_var', 'with_item'):
        exprlist = children[-1]
        names = list(gen_names(exprlist))
        if names:
            namespace.update(names)

    # # NB compile.c makes sure that the default except clause is last
    # except_clause: 'except' [test ['as' NAME]]

    if node_name == 'except_clause':
        if num_children > 1:
            traverse(children[1], namespace, unresolved, unused) # test
        if num_children > 2:
            if get_node_name(children[-1]) == 'NAME':
                name = get_name(children[-1])
                namespace.add(name)
            if python2 and get_node_name(children[-1]) == 'test':
                names = list(gen_names(children[-1]))
                namespace.update(names)
        return

    # suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    #
    # test: or_test ['if' or_test 'else' test] | lambdef
    # test_nocond: or_test | lambdef_nocond
    # lambdef: 'lambda' [varargslist] ':' test
    # lambdef_nocond: 'lambda' [varargslist] ':' test_nocond
    if node_name in ('lambdef', 'lambdef_nocond'):
        namespace = Namespace('<lambda>', namespace)
        if num_children == 4:
            parameters = children[1]
            traverse(parameters, namespace, unresolved, unused)
            arg_names = get_arglist_names(parameters)
            namespace.update(arg_names)
        traverse(children[-1], namespace, unresolved, unused)
        namespace = namespace.get_previous()
        return

    # or_test: and_test ('or' and_test)*
    # and_test: not_test ('and' not_test)*
    # not_test: 'not' not_test | comparison
    # comparison: star_expr (comp_op star_expr)*
    # comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    # star_expr: ['*'] expr
    # expr: xor_expr ('|' xor_expr)*
    # xor_expr: and_expr ('^' and_expr)*
    # and_expr: shift_expr ('&' shift_expr)*
    # shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    # arith_expr: term (('+'|'-') term)*
    # term: factor (('*'|'/'|'%'|'//') factor)*
    # factor: ('+'|'-'|'~') factor | power
    # power: atom trailer* ['**' factor]
    # atom: ('(' [yield_expr|testlist_comp] ')' |
    #        '[' [testlist_comp] ']' |
    #        '{' [dictorsetmaker] '}' |
    #        NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False')

    # testlist_comp: test ( comp_for | (',' test)* [','] )
    if node_name == 'testlist_comp':
        if num_children == 2 and get_node_name(children[1]) == 'comp_for':
            traverse(children[1], namespace, unresolved, unused)
            for child in children:
                if child is not children[1]:
                    traverse(child, namespace, unresolved, unused)
            return

    # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    # subscriptlist: subscript (',' subscript)* [',']
    # subscript: test | [test] ':' [test] [sliceop]
    # sliceop: ':' [test]
    # exprlist: star_expr (',' star_expr)* [',']
    # testlist: test (',' test)* [',']
    # dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
    #                   (test (comp_for | (',' test)* [','])) )
    #

    # classdef: 'class' NAME ['(' [arglist] ')'] ':' suite
    if node_name == 'classdef':
        name = get_name(children[1])
        for n in children[2:-2]:
            traverse(n, namespace, unresolved, unused)
        namespace.add(name)  # a little too early
        namespace = Namespace(name, namespace)
        traverse(children[-1], namespace, unresolved, unused) # suite
        namespace = namespace.get_previous()
        return

    #
    # arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test)
    # argument: test [comp_for] | test '=' test  # Really [keyword '='] test
    if node_name == 'argument':
        if num_children == 3:
            traverse(children[-1], namespace, unresolved, unused)
            return
        if num_children == 2:
            childname = get_node_name(children[1])
            if childname == 'comp_for' or (python2 and childname == 'gen_for'):
                traverse(children[1], namespace, unresolved, unused)

    if python2 and node_name == 'testlist_gexp':
        for child in children:
            if get_node_name(child) == 'gen_for':
                traverse(child, namespace, unresolved, unused)

    if python2 and node_name in 'listmaker':
        for child in children:
            if get_node_name(child) == 'list_for':
                traverse(child, namespace, unresolved, unused)
    #
    # comp_iter: comp_for | comp_if
    # comp_for: 'for' exprlist 'in' or_test [comp_iter]
    if (node_name == 'comp_for' or
        (python2 and node_name in ('gen_for', 'list_for'))):
        exprlist = children[1]
        names = list(gen_names(exprlist))
        assert names
        namespace.update(names)

    # comp_if: 'if' test_nocond [comp_iter]
    #
    # testlist1: test (',' test)*

    # The default traversal of children
    for child in children:
        traverse(child, namespace, unresolved, unused)


def check(filename):
    global_namespace = get_global_namespace()
    try:
        tree = get_tree(filename)
    except SyntaxError:
        e = sys.exc_info()[1]
        lineno = e.lineno
        f = open(filename)
        line = 0
        for x in range(lineno):
            line = f.readline()
        f.close()
        p(filename, "line %s SyntaxError %r" % (e.lineno, line))
        return
    unresolved = dict()
    unused = set()
    traverse(tree, global_namespace, unresolved, unused)
    for line_number, name, namespace in sorted(unresolved.values()):
        if name not in global_namespace:
            msg = '(%s, in %s): %r is undefined.' % (line_number, namespace, name)
            p(filename, msg)
    for name in unused:
        if not name.startswith('_'):
            p("%s: %r is unused" % (filename, name))



def main():
    from optparse import OptionParser
    from os import listdir
    from os.path import join, isdir, isfile, basename

    parser = OptionParser()
    parser.set_description(
        'Check python source files for unknown name errors '
        'and for unused imports. '
        'The arguments name files to check or '
        'directories to check recursively. '
        'If no arguments are given, the current directory '
        'is checked. '
        'If there is a recursion, it excludes ".svn", "build", '
        'and "dist" directories, and includes files that end '
        'in ".py" or ".qpy".')
    (options, args) = parser.parse_args()
    if args:
        todo = args
    else:
        todo = ['.']
    while todo:
        arg = todo.pop()
        if basename(arg) in ['.svn', 'dist', 'build']:
            continue
        elif (isfile(arg) and
              arg in sys.argv or
              (arg.endswith('.py') or
               arg.endswith('.qpy'))):
            check(arg)
        elif isdir(arg):
            todo.extend([join(arg, item) for item in listdir(arg)])

if __name__ == '__main__':
    main()

