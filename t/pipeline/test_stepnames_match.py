import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__)
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))
        
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()

class TestStepnames(TestBase):
    def runTest(self):
        self.fail("fixme: stepnames tests not yet implemented")
        

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestListExpansion)
unittest.TextTestRunner(verbosity=2).run(suite)

