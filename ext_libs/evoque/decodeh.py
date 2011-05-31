"""
Evoque - managed eval-based freeform templating 
Copyright (C) 2007 Mario Ruggier <mario@ruggier.org>
Licensed under the Academic Free License version 3.0
URL: http://evoque.gizmojo.org/
------------------------------------------------------------------------------
$URL: svn://gizmojo.org/pub/evoque/trunk/decodeh.py $

decodeh: heuristically decode a string or text file

$begin{dhdoc} $prefer{filters=[markdown]}

The intention of the *evoque.decodeh* module (part of the ${html.link_evoque()}
distribution) is to conveniently combine a number of ideas and techniques for 
guessing a string's encoding and return a Unicode object. The technique depends
on a codec failing to decode -- but just because a codec succeeds to decode 
a string using a specific encoding does not mean that that encoding is the 
right one. The same bytes representing non-ascii characters are valid in 
several encodings and may thus be decoded to represent wrong characters but 
without giving any Unicode or *RoundTripError*s. The *decodeh* module supports 
two mechanisms to help increase the chances that the guess is the correct one
in the given situation:

The first is control over the encodings to try and in what order. The user may 
specify a list of encodings to try in a *most likely* order, with a default 
such list being provided in the *ENCS* module variable. More likely encodings, 
such as locale defaults, are however always tried prior to the encodings in 
the supplied list. In addition, a single encoding may be explicitly specified 
-- in which case it is *always* tried first.

The second is support for adding any number of encoding-specifc checks to be 
performed *after* a first guess at an encoding, so with a minimized 
performance hit, to check whether there might be a better fitting encoding 
among those still to be tried in the encodings list. If there is, processing 
will jump forward to this position in the encodings list, but if decoding ends
up being unsatisfactory then it will go back and use previous guess. 
The execution of the sequence of checks on a guessed encoding is handled by 
the extensible *may_do_better* mechanism. Checks are user-specifiable via a 
dictionary that defines a sequence of check functions to call per encoding. 
By default, the one used is the provided *MDB* module variable. Each check 
function does a small well-defined check, and may be called anytime that 
specific check is needed. All check functions have the same signature, 
*(s, candidenc)* and must define two list attributes 
*scopencs* and *candidencs*, and return either None (no likely better 
candidate) or a candidate for a more appropriate encoding further along. 

The heart of the *decodeh* module is the *decode_heuristically()* function
that returns the 3-tuple: *(unicode object, encoding used, 
whether deleting chars from input was needed to generate a Unicode object)*

Two other convenient utilities, *decode()* and *decode_from_file()*, are 
provided for the frequent case where all that is cared for is a unicode object. 
If any data had to be lost to generate the unicode object, these two functions 
will by default raise a *RoundTripError*, a sub-type of *UnicodeError*. This 
default behaviour may be modified by specifying the keyword parameter 
*lossy=True* when calling either of these two utilities.

$end{dhdoc}
$begin{dhins} $prefer{filters=[markdown]}

The *decodeh* module was initially inspired by a [similarly named module][skip]
by Skip Montanaro. These other articles or resources have also been 
inspirational and helpful:

- [A Crash Course in Character Encoding][pyzine] 
- [The Absolute Minimum Every Software Developer ... Must Know About ... Character Sets ... ][joel] 
- [A tutorial on character code issues][jukka1] 
- [ISO 8859 material][jukka2] 
- [FAQ: UTF-8, UTF-16, UTF-32 & BOM][bom] 
- [Unicode HOWTO][unihowto]
- threads on comp.lang.python: 
    - [unicode(s, enc).encode(enc) == s?][clp1] 
    - [different encodings for unicode() and u''.encode(), bug?][clp2] 
    - [ValueError: unknown locale: UTF-8][clp4]

[skip]: http://www.webfast.com/~skip/python/decodeh.py "original same-named module from Skip Montanaro"
[pyzine]: http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html "A Crash Course in Character Encoding"
[joel]: http://www.joelonsoftware.com/articles/Unicode.html "The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and Character Sets (No Excuses!)"
[jukka1]: http://www.cs.tut.fi/~jkorpela/chars.html "A tutorial on character code issues"
[jukka2]: http://www.cs.tut.fi/~jkorpela/iso8859/ "ISO 8859 material"
[bom]: http://unicode.org/faq/utf_bom.html "FAQ: UTF-8, UTF-16, UTF-32 & BOM"
[unihowto]: http://www.amk.ca/python/howto/unicode "Unicode HOWTO"
[clp1]: http://groups.google.com/group/comp.lang.python/browse_thread/thread/180f5d9ab7a88cce "unicode(s, enc).encode(enc) == s?"
[clp2]: http://groups.google.com/group/comp.lang.python/browse_thread/thread/2c9c01cebae00c8d "different encodings for unicode() and u''.encode(), bug?"
[clp3]: http://groups.google.com/group/comp.lang.python/browse_thread/thread/b6c2fdcd056aef53 "Is it explicitly specified?"
[clp4]: http://groups.google.com/group/comp.lang.python/browse_thread/thread/b69eaa85aa815af6 "ValueError: unknown locale: UTF-8"
$end{dhins}
"""
# $begin{decodeh}
__revision__ = "$Id: decodeh.py 1153 2009-01-20 11:43:21Z mario $"

import sys, codecs, locale, re

if sys.version < '3':
    bytes = str
else:
    unicode = str

class RoundTripError(UnicodeError):
    pass

# for clarity between py2 and py3, the variable name "b" refers to a
# py2 or py3 bytestring, and "s" refers to a py2 unicode or a py3 str.

# for py3, the values returned by codecs.BOM_* is a bytes object
UTF_BOMS = [
    (getattr(codecs, 'BOM_UTF8', '\xef\xbb\xbf'), 'utf_8'),
    (getattr(codecs, 'BOM_UTF16_LE', '\xff\xfe'), 'utf_16_le'), # utf-16
    (getattr(codecs, 'BOM_UTF16_BE', '\xfe\xff'), 'utf_16_be'),
    #(getattr(codecs, 'BOM_UTF32_LE', '\xff\xfe\x00\x00'), 'utf_32_le'), # utf-32
    #(getattr(codecs, 'BOM_UTF32_BE', '\x00\x00\xfe\xff'), 'utf_32_be')
]
def get_bom_encoding(b):
    """ (b:bytes) -> either((None, None), (bom:bytes, encoding:str)) 
    """
    for bom, encoding in UTF_BOMS:
        if b.startswith(bom):
            return bom, encoding
    return None, None

def is_lossy(b, enc, s=None):
    """ (b:bytes, enc:str, s:either(str, None)) -> bool 
    Return False if a decode/encode roundtrip of byte string s does not lose 
    any data. If s is not None, it is expected to be the unicode string 
    given by b.decode(enc).
    
    Note that this will, incorrectly, return True for cases where the 
    encoding is ambiguous, e.g. is_lossy("\x1b(BHallo","iso2022_jp"), 
    see comp.lang.python thread "unicode(s, enc).encode(enc) == s ?".
    """
    if s is None:
        s = b.decode(enc)
    if s.encode(enc) == s:
        return False
    else:
        return True

# may_do_better post-guess checks

def may_do_better(b, encodings, guenc, mdb):
    """ Processes the mdb conf object and returns None or a best candidate
    """
    funcs = mdb.get(guenc)
    if funcs is None:
        return None
    # candidencs not in encodings or appearing before guenc are ignored
    guenc_index = encodings.index(guenc)
    for func in funcs:
        for candidenc in func.candidencs:
            if not candidenc in encodings:
                continue
            if guenc_index > encodings.index(candidenc):
                continue
            cenc = func(b, candidenc) 
            if cenc is not None:
                return cenc

def compiled_re(pattern):
    """ (raw_pattern:either(bytes, str)) -> the compiled RE for pattern
    For py3, we cannot match a str pattern on a bytes object:
        TypeError: can't use a string pattern on a bytes-like object
    Whether pattern is a py2/py3 bytes or unicode pattern, the resulting
    compiled re always corresponds.
    """
    return re.compile(bytes(pattern.encode()))

# ASCII chars in range below never appear in text 
def _ascii_non_text(b, candidenc):
    if _ascii_non_text.re.search(b) is not None:
        return candidenc
_ascii_non_text.scopencs = ["ascii"]
_ascii_non_text.candidencs = ["BINARY"]
_ascii_non_text.re = compiled_re(r"[\x00-\x06\x0b\x0e-\x1f\x7f]")

# ISO 2022 ESC sequences are more likely to be used in ISO 2022 encodings 
def _iso2022_jp_escapes(b, candidenc):
    if _iso2022_jp_escapes.re.search(b) is not None:
        return candidenc
_iso2022_jp_escapes.scopencs = ["ascii"]
_iso2022_jp_escapes.candidencs = ["iso2022_jp"]
_iso2022_jp_escapes.re = compiled_re(r"\x1b\(B|\x1b\(J|\x1b\$@|\x1b\$B")

# the latin_1 control chars 0x80 to 0x9F (but not 0x85) are displayable in 
# non-ISO extended ASCII (Mac, IBM PC) most likley candidate being cp1252 
def _latin_1_control_chars(b, candidenc):
    if _latin_1_control_chars.re.search(b) is not None:
        return candidenc
_latin_1_control_chars.scopencs = ["latin_1"]
_latin_1_control_chars.candidencs = ["cp1252"]
_latin_1_control_chars.re = compiled_re(r"[\x80-\x84\x86-\x9f]")

# Chars in range below are more likely to be used as symbols in iso8859_15
def _iso8859_15_symbols(b, candidenc):
    if _iso8859_15_symbols.re.search(b) is not None:
        return candidenc
_iso8859_15_symbols.scopencs = ["latin_1", "cp1252"]
_iso8859_15_symbols.candidencs = ["iso8859_15"]
_iso8859_15_symbols.re = compiled_re(r"[\xa4\xa6\xa8\xb4\xb8\xbc-\xbe]")

# user specifiable parameters - defaults

# The default list of encodings to try (after "ascii" and "utf_8"). 
# Order matters! Encoding names use the corresponding python codec name, 
# as listed at: http://docs.python.org/lib/standard-encodings.html
ENCS = [
    "latin_1", # add other iso-8859 encodings 
    "cp1252", # add other Windows/Mac encodings
    "iso8859_15", 
    "mbcs", 
    "big5", "euc_jp", "euc_kr", "gb2312", "gbk", "gb18030", "hz", 
    "iso2022_jp", "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_3", 
        "iso2022_jp_2004", "iso2022_jp_ext", "iso2022_kr",
    "koi8_u", "ptcp154", "shift_jis" ]

# Encoding to ignore
IGNORE_ENCS = [None, "cp0"]

# Dictionary specifying the may_do_better checks per encoding. Whenever any 
# of the following functions returns a non-None candidenc value, the algorithm 
# will skip forward to the value's position in the encodings list. 
# For any function here to be executed, its target candidenc must be in the 
# list of encodings passed to _decode_heuristically().  
MDB = {
    "ascii": [
        # _ascii_non_text, # likely to be binary
        _iso2022_jp_escapes, 
    ],
    "latin_1": [
        _latin_1_control_chars, 
        _iso8859_15_symbols, 
    ], 
    # may refine with further tests to discern which ISO Latin encoding
    "cp1252": [
        _iso8859_15_symbols,
    ], 
    # may refine with further tests to discern which Windows/Mac encoding
}

# user callable utilities

def decode_from_file(filename, enc=None, encodings=ENCS, mdb=MDB, lossy=False):
    """ (filename:str, enc:str, encodings:list, mdb:dict, lossy:bool) -> str
    Convenient wrapper on decode(str) for reading a text file.
    """
    # We open the file in binary mode, and let the algorithm do the guesswork
    b = open(filename, 'rb').read()
    return decode(b, enc=enc, encodings=encodings, mdb=mdb, lossy=lossy)

def decode(bs, enc=None, encodings=ENCS, mdb=MDB, lossy=False):
    """ (bs:either(bytes, str), enc:str, encodings:list, mdb:dict, 
                lossy:bool) -> str
    Raises RoundTripError when lossy=False and re-encoding the string
    is not equal to the input string. 
    """
    s, enc, loses = decode_heuristically(bs, enc=enc, encodings=encodings, mdb=mdb)
    if not lossy and loses:
        raise RoundTripError("Data loss in decode/encode round trip")
    else:
        return s
    
def decode_heuristically(bs, enc=None, encodings=ENCS, mdb=MDB):
    """ (bs:either(bytes, str), enc:str, encodings:list, mdb:dict) -> 
                                            (x:unicode, enc:str, lossy:bool)
    Tries to determine the best encoding to use from a list of specified 
    encodings, and returns the 3-tuple: a unicode object, the encoding used, 
    and whether deleting chars from input was needed to generate a Unicode 
    object. The list of all encodings to be considered is prepared once and is 
    then passed on for actual processing (recursive). 
    """
    if isinstance(bs, unicode):
        # nothing to do
        return bs, "utf_8", False 
    # At this point, bs is therefore necessarily a byte string.
    # A priori, the byte string may be in a UTF encoding and may have a BOM
    # that we may use but that we must also remove. 
    bom, bom_enc = get_bom_encoding(bs)
    if bom is not None:
        bs = bs[len(bom):]
    # Order is important: encodings should be in a *most likely* order. 
    # Thus, we always try first:
    # a) any caller-provided encoding 
    # b) encoding from UTF BOM 
    # c) ascii, common case and is unambiguous if no errors
    # d) utf_8 
    # e) system default encoding
    # f) any encodings we can glean from the locale
    precedencs = [enc, bom_enc, "ascii", "utf_8", sys.getdefaultencoding()]
    try: precedencs.append(locale.getpreferredencoding())
    except AttributeError: pass
    try: precedencs.append(locale.nl_langinfo(locale.CODESET))
    except AttributeError: pass
    try: precedencs.append(locale.getlocale()[1])
    except (AttributeError, IndexError): pass
    try: precedencs.append(locale.getdefaultlocale()[1])
    except (AttributeError, IndexError, ValueError): pass
    # Build list of encodings to process, normalizing on lowercase names
    # and avoiding any None and duplicate values.
    precedencs = [ e.lower() for e in precedencs if e not in IGNORE_ENCS ]
    allencs = []
    for e in precedencs:
        if e not in allencs:
            allencs.append(e)
    allencs += [ e for e in encodings if e not in allencs ]
    # Check integrity of the mdb dict
    for guenc, funcs in mdb.items():
        for func in funcs:
            assert guenc in func.scopencs
    return _decode_heuristically(bs, allencs, mdb)

def _decode_heuristically(b, allencs, mdb):
    """ Recursive function to loop over and examine each encoding in allencs.
    """
    eliminencs = []
    for enc in allencs:
        try:
            # for py3, s may only be a bytes object
            s = b.decode(enc)
        except (UnicodeError, LookupError):
            eliminencs.append(enc)
            continue
        else:
            candidenc = may_do_better(b, allencs, enc, mdb)
            if candidenc is not None:
                # recurse to process from candidenc's position in allencs
                y, yenc, loses = _decode_heuristically(b, 
                                       allencs[allencs.index(candidenc):], mdb)
                if not loses:
                    return y, yenc, False
            return s, enc, False
    # no enc worked - try again, using "ignore" parameter, return longest
    if eliminencs:
        allencs = [ e for e in allencs if e not in eliminencs ]
    output = [(s.decode(enc, "ignore"), enc) for enc in allencs]
    output = [(len(s[0]), s) for s in output]
    output.sort()
    s, enc = output[-1][1]
    if not is_lossy(s, enc, s):
        return s, enc, False
    else:
        return s, enc, True
