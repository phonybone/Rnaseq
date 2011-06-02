"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/__main__.py $
$Id: __main__.py 30591 2008-03-13 15:39:38Z dbinger $
"""
from qpy.compile import compile
import sys

args = sys.argv[1:]
if not args:
    sys.stdout.write("no files to compile\n")
else:
    for filename in args:
        compile(filename)
