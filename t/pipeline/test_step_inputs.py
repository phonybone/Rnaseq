import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset.load(RnaseqGlobals.root_dir+'/t/fixtures/readset/readset1.syml')

    def test_setup(self):
        self.assertEqual(self.readset.name, 'test_readset')



suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


        

