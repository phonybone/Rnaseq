import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)

class TestBasic(TestCreate):
    def runTest(self):
        readset=Readset(filename='readset.syml')
        self.assertEqual(readset.suffix, 'syml')
        self.assertEqual(readset.type, 'readset')
        

        readset.load()
        print "readset after .load(): %s" % readset
        self.assertEqual(readset.__class__,Readset)

class TestMissingReadset(TestCreate):
    def runTest(self):
        #with self.assertRaises(UserError):
        try:
            readset=Readset(filename='missing').load()
        except UserError:
            print "yay!"

class TestMissingReadsetArg(TestCreate):
    def runTest(self):
        #with self.assertRaises(AssertionError):
        try:
            readset=Readset().load()
        except ProgrammerGoof:
            print "TestMissingReadsetArg: yay!"



if __name__=='__main__':
    unittest.main()

