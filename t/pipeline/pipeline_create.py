import unittest
from Rnaseq import *
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        Templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../fixtures/templates")


class TestGood(TestCreate):
    def runTest(self):
        readset=Readset(name='readset').load()
        p=Pipeline(name='test', readset=readset)
        self.assertEqual(p.__class__,Pipeline)


class TestBad(TestCreate):
    def runTest(self):
        readset=Readset(name='readset').load()
        with self.assertRaises(UserError):
            p=Pipeline(name='test', readset=readset).load()

            

if __name__=='__main__':
    unittest.main()

