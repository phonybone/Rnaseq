import unittest, sys, os

if os.path.dirname(__file__)=='':       # running in local directory
    root_dir=(os.path.normpath(os.getcwd()+'/../..'))
else:
    root_dir=(os.path.normpath(os.path.dirname(__file__)+'/../..'))
sys.path.append(os.path.join(root_dir, 'lib'))
sys.path.append(os.path.join(root_dir, 'ext_libs'))

from Rnaseq import *

suite=unittest.TestLoader().discover('.',pattern='test*.py')
unittest.TextTestRunner(verbosity=2).run(suite)
