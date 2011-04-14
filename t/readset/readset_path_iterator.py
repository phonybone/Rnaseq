import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)

class TestPathIterator(TestCreate):
    def runTest(self):
        readset=Readset(filename='readset.syml').load()
        path_it=readset.path_iterator()
        self.assertEqual(len(path_it),3)
        for path in path_it:
            print "path is %s" % path





if __name__=='__main__':
    unittest.main()

