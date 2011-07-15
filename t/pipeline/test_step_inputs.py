import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

# Not sure what this was meant to test exactly...
class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]

    def test_setup(self):
        self.assertEqual(self.readset.name, 'readset1.syml')



suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


        

