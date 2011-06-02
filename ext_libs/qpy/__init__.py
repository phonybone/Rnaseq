"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/__init__.py $
$Id: __init__.py 31745 2009-07-20 21:21:48Z dbinger $
Copyright (c) Corporation for National Research Initiatives 2009. All Rights Reserved.
"""
__version__ = "1.8"

import sys

try:
    from qpy.quoted import xml, join_str, join_xml, xml_quote
    [xml, join_str, join_xml, xml_quote] # for checker.
except ImportError:
    sys.stdout.write("qpy %s\n" % __version__)
    xml = None

# The remainder is for partial compatibility with previous release.
h8 = xml
import sys
if sys.version.startswith("3"):
    stringify = str
    u8 = str
else:
    from __builtin__ import unicode, basestring # for checker.
    u8 = unicode

    def stringify(obj):
        """(obj) -> basestring
        Return a string version of `obj`.  This is like str(), except
        that it tries to prevent turning str instances into unicode instances.
        The type of the result is either str or unicode.
        """
        tp = type(obj)
        if issubclass(tp, basestring):
            return obj
        elif hasattr(tp, '__unicode__'):
            s = tp.__unicode__(obj)
            if not isinstance(s, basestring):
                raise TypeError('__unicode__ did not return a string')
            return s
        elif hasattr(tp, '__str__'):
            s = tp.__str__(obj)
            if not isinstance(s, basestring):
                raise TypeError('__str__ did not return a string')
            return s
        else:
            return str(obj)
