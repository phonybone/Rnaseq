import unittest, sys, os


#sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../lib')))
#sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../ext_libs')))
from Rnaseq import *

suite=unittest.TestLoader().discover('.',pattern='test*.py')
unittest.TextTestRunner(verbosity=2).run(suite)
