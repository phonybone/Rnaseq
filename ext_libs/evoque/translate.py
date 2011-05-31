'''
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
'''
__url__ = "$URL: svn://gizmojo.org/pub/evoque/trunk/translate.py $"
__revision__ = "$Id: translate.py 1153 2009-01-20 11:43:21Z mario $"

import os, re
from sys import exc_info
from binascii import hexlify

COMMASPACE = ", "

def strip_quotes(s):
    """ (s:basestring) -> str 
    If the actual literal string s is enclosed in quotes, get rid of them.
    Note: simplistic e.g literal strings <"abc>, <'"abc>, <"'abc"'>, <'"abc'">
    will all be stripped to <abc>. 
    """
    return s.strip().strip('"\'')

def randbytes(num_bytes):
    """ (num_bytes:int) -> bytes
    Return a random byte str of length num_bytes
    """
    return hexlify(os.urandom(num_bytes))

def get_unique_marker(s, num_bytes=4):
    """ Get a string marker guaranteed to be unique in s 
    """
    marker = randbytes(num_bytes).decode()
    # ensure never occurs in s 
    if s.find(marker) != -1:
        return get_unique_marker(s)
    return marker 

class _UnpackGlobals(dict):
    def __getitem__(self, name):
        return name
def unpack_symbol(symbol, globals=_UnpackGlobals()):
    """ If compound symbol (list, tuple, nested) unpack to atomic symbols """
    return eval(symbol, globals, None)

# RE template for directives: $keyword{ expr } or $keyword{% expr %}
BASE_RE = r'\$%(k)s\{(%%)?\s*(?P<x>.*?[^\}])\s*(?(1)%%)\}'
# RE template for begin/end + specific "label"
BASE_RE_LABEL = r'\$%(k)s\{(%%)?\s*%(v)s\s*(?(1)%%)\}'
# Pre-compiled Regular Expressions
SLURPL = re.compile(r'^[ \t\r\f\v]*\n')
SLURPR = re.compile(r'\n[ \t\r\f\v]*$')
RE_TEST = re.compile(BASE_RE % dict(k="test"), re.DOTALL)
RE_PREFER = re.compile(BASE_RE % dict(k="prefer"), re.DOTALL)
RE_OVERLAY = re.compile(BASE_RE % dict(k="overlay"), re.DOTALL)
RE_EVOQUE = re.compile(BASE_RE % dict(k="evoque"), re.DOTALL)
RE_BEGIN = re.compile(BASE_RE % dict(k="begin"), re.DOTALL)
RE_END = re.compile(BASE_RE % dict(k="end"), re.DOTALL)
RE_SVN_KW = re.compile(r'\$(URL|Id|Revision|Author|Date):[^$\n]*\$')

class Translator(object):
    """ Translator from $-syntax to %-syntax
    """
    def __init__(self, collection):
        self.collection = collection
        # globals = self.collection.domain.globals
        # slurpy_directives = self.collection.slurpy_directives
    
    def get_re_label(self, key, label):
        """ (key:either("begin", "end"), label:str) -> re 
        """
        return BASE_RE_LABEL % dict(k=key, v=label)
    
    def extract_nested(self, ts, label, strip=False):
        """ (ts:str, label:str) -> ts:str 
        Extract the substring delineated with $begin{label} and $end{label}.
        If begin/end pattern not present, take from begin/end of string. 
        If label is None, use entire string. 
        If strip==True return the "complement" of nested substring.
        """
        begin = re.search(self.get_re_label("begin", label), ts)
        end = re.search(self.get_re_label("end", label), ts)
        bi, bj = None, None
        ei, ej = None, None
        if begin is not None:
            bi, bj = begin.span()
        if end is not None:
            ei, ej = end.span()
        if strip:
            # slurpy remove all, including outer begin/end delineators
            return self.slurpy_splice(ts, bi, ej)
        # slurpy extract the inner contents delineated with begin/end
        return self.slurpy_strip(ts[bj:ei])
    
    def strip_nested(self, ts, labels):
        """ (ts:str, labels:[str]) -> ts:str 
        Strip out the substrings delineated with $begin{label} and $end{label}.
        Append each label to labels.
        """
        match = RE_BEGIN.search(ts) or RE_END.search(ts)
        if match is not None:
            label = match.group("x")
            if label in labels:
                raise SyntaxError("Cannot re-use begin/end label [%s]" % 
                        match.group(0))
            labels.append(label)
            ts = self.strip_nested(
                    self.extract_nested(ts, label, strip=True), labels)
        return ts
    
    def strip_comments(self, ts):
        """ (ts:str) -> ts:str 
        Consume string inside out, i.e. work right/innermost->left/outwards
        """
        i = ts.rfind("#[")
        j = ts.find("]#", i)
        if i == -1 and j == -1:
            return ts
        elif (i != -1 and j != -1):
            return self.strip_comments(self.slurpy_splice(ts, i, j+2))
        else:
            raise SyntaxError("Unbalanced open and close comment markers.")
    
    def extract_test_data(self, ts, test_data):
        """ (ts:str, test_data:[{}]) -> ts:str
        Returns the ts with any test directives removed, 
        and for each one found will update the input test_data parameter.
        """
        match = RE_TEST.search(ts)
        if match is not None:
            try:
                test_data.append(self.geval("dict("+match.group("x")+")"))
            except (SyntaxError,):
                raise SyntaxError("%s : %s" % (match.group(0), exc_info()[1]))
            ts = self.slurpy_splice(ts, *match.span())
            ts = self.extract_test_data(ts, test_data)
        return ts
    
    def extract_prefer(self, ts):
        """ (ts:str) -> (prefer:either(None, {}), ts:str) 
        """
        prefer = None
        for match in RE_PREFER.finditer(ts):
            if prefer is not None:
                raise SyntaxError("Only one prefer directive allowed [%s]" % (
                        match.group(0)))
            try:
                prefer = self.geval("dict("+match.group('x')+")")
            except (SyntaxError,):
                raise SyntaxError("%s : %s" % (match.group(0), exc_info()[1]))
            for key in prefer:
                if key not in ("raw", "data", "quoting", "filters"):
                    raise SyntaxError("%s : %s" % (match.group(0), key))
            ts = self.slurpy_splice(ts, *match.span())
        return prefer, ts
    
    def directive_first_arg(self, expr, kw="name"):
        """ (expr:str, kw:str) -> (kw, value, other_params)
        Expects expr to be a parameter csv string, where the first value is:
        - either a non-keyworded literal str (that may or may not be quoted)
        - or a keyworded expression str (thus with actual value given by 
          ${expression} at runtime)
        """
        # splitting on "," may be too simplistic
        first_and = expr.split(",", 1)
        kw_v = first_and[0].split("=") #+ py>=2.5, partition()
        other_params = "".join(first_and[1:]).strip()
        if other_params:
            other_params = COMMASPACE + other_params
        if len(kw_v) == 1:
            # whether enclosed in quotes or not, value is a literal
            return kw, repr(strip_quotes(kw_v[0])), other_params
        else:
            # len must be 2; value may be a literal or a var name
            keyword, value = kw_v[0].strip(), kw_v[1].strip()
            assert keyword == kw
            return keyword, value, other_params
    
    def extract_overlay(self, ts):
        """ (ts:str) -> (eval_overlay:str), ts:str) 
        """
        eval_overlay = None
        for match in RE_OVERLAY.finditer(ts):
            if eval_overlay is not None:
                raise SyntaxError(("Only one overlay directive allowed "
                        "[%s]") % (match.group(0)))
            try:
                expr = match.group('x')
                kw, value, other_params = self.directive_first_arg(expr)
                eval_overlay = "%s=%s%s" % (kw, value, other_params)
            except (SyntaxError, AssertionError):
                raise SyntaxError("%s : %s" % (match.group(0), exc_info()[1]))
            ts = self.slurpy_splice(ts, *match.span())
        return eval_overlay, ts
    
    def evoque_directive_to_expr(self, ts):
        """ (ts:str) -> ts:str 
        """
        match = RE_EVOQUE.search(ts)
        if match is not None:
            try:
                expr = match.group('x')
                kw, value, other_params = self.directive_first_arg(expr)
            except (SyntaxError, AssertionError):
                raise SyntaxError("%s : %s" % (match.group(0), exc_info()[1]))
            i, j = match.span()
            ts = self.evoque_directive_to_expr(self.slurpy_splice(ts, i, j, 
                replacement="${evoque(%s=%s%s)}" % (kw, value, other_params)))
        return ts
    
    def prepare_svn_keywords(self, ts):
        """ (ts:str) -> ts:str : double $ in expanded svn keywords 
        """
        def match(m):
            return m.group(0).replace("$", "$$")
        return RE_SVN_KW.sub(match, ts)
    
    def translate(self, ts):
        """ (ts:str) -> (labels:[], prefer:either(None, {}), 
                    eval_overlay:str, test_data:[{}], str)
        Translate template string ts from $-syntax to %-syntax 
        """
        ## strip out src template code not needed for this template runtime
        # svn keywords
        ts = self.prepare_svn_keywords(ts)
        # literal "$" (doubled)
        ts = ts.replace("$$", "_UNICHR_36_")
        # remove consumed newlines 
        ts = ts.replace("\\\n", "")
        # strip comments
        ts = self.strip_comments(ts)
        # strip any other nesteds
        labels = []
        ts = self.strip_nested(ts, labels)
        ## From this point on ts is really *this* template's string
        prefer, ts = self.extract_prefer(ts)
        eval_overlay, ts = self.extract_overlay(ts)
        ts = self.evoque_directive_to_expr(ts)
        test_data = []
        ts = self.extract_test_data(ts, test_data)
        marker = get_unique_marker(ts)
        consumed = []
        # at this point ts may only contain: $if{}, $for{} and ${}
        ts = self._translate(ts, marker, consumed)
        consumed.reverse()
        ts = self.unplacehold(ts, marker, consumed)
        return (labels, prefer, eval_overlay, test_data, 
                ts.replace("_UNICHR_36_", "$"))
    
    def _translate(self, ts, marker, consumed, lmph=None, rmph=None):
        """ (ts:str, marker:str, consumed:[str], lmph:str, rmph:str) -> str
        Assume the template (sub-)string ts here has no begin/end blocks or
        comments left, thus only need to handle if & for directives (that
        may be nested). Consume ts inside out, i.e. work recursively 
        right/innermost->left/outwards. 
        """
        nexts = [ (ts.rfind("$if{"), "if", self.parse_if), 
                  (ts.rfind("$for{"), "for", self.parse_for) ]
        nexts.sort()
        start, token, directive_parser = nexts[-1]
        if start > -1:
            j, data = directive_parser(ts, start)
            placeholder = self.placehold(marker, token, consumed, data)
            ts = self.slurpy_splice(ts, start, j, placeholder)
            lmph = lmph or placeholder # leftmost placeholder
            rmph = rmph or placeholder # rightmost placeholder
            phi = ts.index(placeholder)
            # lmph, rmph may have been nested, and placeholdered away
            if lmph not in ts or phi < ts.index(lmph) :
                lmph = placeholder
            if rmph not in ts or ts.index(rmph) < phi:
                rmph = placeholder
            ts = self._translate(ts, marker, consumed, lmph, rmph)
        elif start == -1:
            ts = self.translate_text(ts)
        return ts
    
    def placehold(self, marker, token, consumed, data):
        # to avoid recursion on consumed blocks 
        placeholder = "%s%s" % (marker, len(consumed))
        consumed.append([placeholder, token, data ])
        return placeholder
    
    def unplacehold(self, ts, marker, consumed):
        if ts.find(marker) != -1:
            for i, (placeholder, token, data) in enumerate(consumed):
                if token == "if":
                    s = self.unplacehold_if(data, marker, consumed[i+1:])
                elif token == "for":
                    s = self.unplacehold_for(data, marker, consumed[i+1:])
                else:
                    s = data
                ts = ts.replace(placeholder, s)
        return ts
    
    def unplacehold_if(self, data, marker, consumed):
        """ (data:[[[cond, str]], str ], marker:str, consumed:[]) 
                -> str version of (((cond, str),), str)
        """
        for if_cs in data[0]:
            if_cs[1] = self.unplacehold(if_cs[1], marker, consumed)
        data[1] = self.unplacehold(data[1], marker, consumed)
        return "%%(_evoque_if(%s))s" % COMMASPACE.join([
                    self.write_cond_strs(data[0]), repr(data[1])])
    def write_cond_str(self, cond, s):
        return "(%s, %s)" % (cond, repr(s))
    def write_cond_strs(self, cond_strs):
        return "(%s,)" % COMMASPACE.join([ self.write_cond_str(*cs) 
                                            for cs in cond_strs ])
    
    def unplacehold_for(self, data, marker, consumed):
        """ (data:[mup:bool, either(symbol, sequence(symbol)), iterator, 
                   str, str], marker:str, consumed:[]) -> str
        """
        for i in (3,4):
            data[i] = self.unplacehold(data[i], marker, consumed)
        _evoque_for_func_name = "_evoque_for"
        if data[0]: # Multiple UnPack 
            _evoque_for_func_name = "_evoque_for_mup"
        return "%%(%s(%s))s" % (_evoque_for_func_name, COMMASPACE.join([
                    repr(data[1]), data[2], repr(data[3]), repr(data[4])]))
    
    def geval(self, expr):
        """ (expr:str) -> anything 
        Evaluate expr strictly under the domain's globals
        """
        return eval(expr, self.collection.domain.globals, None)
    
    def slurpy_splice(self, ts, i, j, replacement=""):
        """ (ts:str, i:int, j:int, replacement:str) -> str 
        Splice replacement into ts, instead of whitespace+ts[i:j]+whitespace.
        """
        return self.slurpy_strip(ts[:i], "right") + replacement + \
                self.slurpy_strip(ts[j:], "left")
    
    def slurpy_strip(self, ts, lr=None):
        """ (ts:str, lr=either(None, "left", "right")) -> str
        If slurpy_directives, slurpy strip ts:
        - on left or right or both (None), of whitespace up-to first newline
        - on left (only), of first \n
        """
        if self.collection.slurpy_directives:
            if lr is None or lr=="left":
                ts = SLURPL.sub("", ts, 1)
            if lr is None or lr=="right":
                ts = SLURPR.sub("\n", ts, 1)
        return ts

    # the input template string s received by the parse methods below is 
    # guaranteed to not have any nested blocks
    
    def get_offset_closing(self, s, start, opening):
        """ (s:str, start:int, opening:str) -> 
                expr_offset:int, expr_closing:either("}", "%}"))
        For the template string s, given a directive opening such as "$for{", "$if{", 
        determine 
        a) the directive's expression offset (from start) 
        b) the directive ending, whether "}" or "%}"
        """
        offset, closing = len(opening), "}"
        if (len(s)>start+offset) and s[start+offset] == "%":
            closing = "%}"
        return offset, closing
    
    def parse_if(self, s, start):
        """ (s:str, start:int) -> 
                consumes_upto:int, if_data:[[[cond, str]], str]
        if_data:
          if_cond_str: [(condition, template)] for the if and any elif blocks
          otherwise: the else template
        """
        offset, closing = self.get_offset_closing(s, start, "$if{")
        stext = s[start+offset:]
        j = stext.find("$fi")
        if j == -1:
            raise SyntaxError("No closing $fi for $if{} block.")
        stexts = stext[:j].split("$else")
        if len(stexts) > 2: 
            raise SyntaxError("More than one $else clause in $if{}/$fi block.")
        selse = self.slurpy_strip("".join(stexts[1:]))
        if selse:
            selse = self.translate_text(selse)
        ifcs = [ self.parse_xt(xt) for xt in stexts[0].split("$elif{") ]
        return start+offset+j+3, [ifcs, selse]
    
    def parse_for(self, s, start):
        """ (s:str) -> consumes_upto:int, for_data:[
                mup:bool, symbol:either(symbol, sequence(symbol)), 
                iterator, body:str, otherwise:str] 
        for_data:
          mup: requires multiple-unpack loop variable(s) (cache for runtime).
          symbol: the name or the sequence of names for the loop variable(s).
          iterator: the sequence we are looping on. 
          body: the template to repeat for each item.
          otherwise: if list is empty, then output this template. 
        """
        offset, closing = self.get_offset_closing(s, start, "$for{")
        stext = s[start+offset:]
        j = stext.find("$rof")
        if j == -1:
            raise SyntaxError("No closing $rof for $for{} block.")
        stexts = stext[:j].split("$else")
        if len(stexts) > 2:
            raise SyntaxError("More than one $else clause in $for{}/$rof block.")
        selse = self.slurpy_strip("".join(stexts[1:]))
        if selse:
            selse = self.translate_text(selse)
        sfor = self.parse_xt(stexts[0])
        symbol, seq = [ ss.strip() for ss in sfor[0].split(' in ') ]
        symbols = unpack_symbol(symbol)
        return start+offset+j+4, [symbol!=symbols, symbols, seq, sfor[1], selse]
    
    def parse_xt(self, s):
        """ (s:str) -> (expr:str, text:str)
        Process a expr_text string: "<expr>}<text>" or "<expr>%}<text>"
        """
        offset, closing = self.get_offset_closing(s, 0, "")
        close = s.index(closing)
        expr = s[:close].strip()
        text = self.translate_text(self.slurpy_strip(s[close+len(closing):]))
        return [expr, text]
        
    def translate_text(self, s):
        """ s guaranteed may only contain expressions: ${ <expr> } 
        """
        t, pieces = [], s.split("$")
        for i, piece in enumerate(pieces):
            t.append(self._text_piecewise(i, piece))
        return "".join(t)
    def _text_piecewise(self, i, p):
        """ translate a $-removed piece from $-syntax to %-syntax 
        """
        if p.startswith('{'):
            offset, closing = self.get_offset_closing(p, 0, "{")
            close = p.index(closing)
            expr_format = p[len(closing):close].split("!", 1)
            expr, format = expr_format[0], (expr_format[1:] or ["s"])[0]
            remainder = p[close+len(closing):].replace("%", "%%")
            return "%("+expr.strip()+")" + format.strip() + remainder
        else:
            if i != 0:
                raise SyntaxError('Unescaped "$" literal at: "$%s"' %(p))
            return p.replace("%", "%%")
    
