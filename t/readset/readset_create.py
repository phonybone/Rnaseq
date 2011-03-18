import unittest
from Rnaseq import *
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")

class TestBasic(TestCreate):
    def runTest(self):
        readset=Readset(name='readset').load()
        self.assertEqual(readset.__class__,Readset)

class TestMissingReadset(TestCreate):
    def runTest(self):
        with self.assertRaises(UserError):
            readset=Readset(name='missing').load()


class TestMissingReadsetArg(TestCreate):
    def runTest(self):
        with self.assertRaises(AssertionError):
            readset=Readset().load()



if __name__=='__main__':
    unittest.main()

