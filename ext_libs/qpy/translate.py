"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/translate.py $
$Id: translate.py 30587 2008-03-13 10:55:08Z dbinger $
"""
from parser import expr, suite
from pprint import pprint
from symbol import sym_name
from token import tok_name
import re
import sys
import symbol

_annotation_re = re.compile(
    r"^(?P<indent>[ \t]*)def(?:[ \t]+)"
    r"(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)"
    r"(?:[ \t]*:[ \t]*)(?P<type>xml|str)(?:[ \t]*)"
    r"(?:[ \t]*[\(\\])",
    re.MULTILINE|re.VERBOSE)

_template_re = re.compile(
    r"^(?P<indent>[ \t]*) def (?:[ \t]+)"
    r" (?P<name>[a-zA-Z_][a-zA-Z_0-9]*)"
    r" (?:[ \t]*) \[(?P<type>plain|html)\] (?:[ \t]*)"
    r" (?:[ \t]*[\(\\])",
    re.MULTILINE|re.VERBOSE)

def translate_tokens(buf):
    """
    def f:xml( ... )  -> def f__xml_template__(...):
    def f:str( ... )  -> def f__str_template__(...):

    and, for backward compatibility,

    def foo [html] (...): -> def foo__xml_template__(...):
    def foo [plain] (...): -> def foo__str_template__(...):
    """
    def replacement(match):
        if match.group('type') in ('xml', 'html'):
            template_type = 'xml'
        elif match.group('type') in ('str', 'plain'):
            template_type = 'str'
        return '%sdef %s__%s_template__(' % (match.group('indent'),
                                 match.group('name'),
                                 template_type)
    translated = _annotation_re.sub(replacement, buf)
    translated = _template_re.sub(replacement, translated)    
    return translated

def get_parse_tree(source, source_name=None):
    try:
        if source_name is None:
            return expr(source).tolist(True)
        else:
            return suite(source).tolist(True)
    except (TypeError, SyntaxError):
        e = sys.exc_info()[1]
        e.filename = source_name
        raise e

def statement_tree(stmt):
    tree = get_parse_tree(stmt, 'fake')[1]
    assert tree[0] == symbol.stmt
    return tree

def expr_tree(x):
    tree = get_parse_tree(x)[1]
    assert tree[0] == symbol.testlist
    return tree

def get_power(node):
    n = node
    while n[0] != symbol.power:
        n = n[1]
    return n

def symtree(t):
    if not isinstance(t, list):
        return t
    if t[0] in sym_name:
        return [(sym_name.get(t[0]), t[0])] + list(map(symtree, t[1:]))
    elif t[0] in tok_name:
        return [(tok_name.get(t[0]), t[0])] + list(map(symtree, t[1:]))
    else:
        assert 0, t

def ptree(t):
    pprint(symtree(t))
