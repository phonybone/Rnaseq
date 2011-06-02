#!/usr/bin/env python
import sys
from qpy.compile import get_code
if __name__ == '__main__':
    file_name = sys.argv[1]
    code = get_code(open(file_name).read(), file_name)
    eval(code, dict(__name__='__main__', __file__=file_name))

