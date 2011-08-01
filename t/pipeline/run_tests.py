import unittest, sys, os

sys.path.insert(0,os.path.abspath(__file__+'/../../../lib'))
from Rnaseq import *

suite=unittest.TestLoader().discover('.',pattern='test*.py')
unittest.TextTestRunner(verbosity=2).run(suite)
