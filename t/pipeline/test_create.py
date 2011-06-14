import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)


class TestBasicCreate(TestCreate):
    def runTest(self):
        readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))
        p=Pipeline(name='test', readset=readset)
        self.assertEqual(p.__class__,Pipeline)
        

class TestMissingTemplate(TestCreate):
    def runTest(self):
        readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))
        with self.assertRaises(UserError):
            p=Pipeline(name='test', readset=readset).load() # no template pipeline/test.syml


class TestLoad(TestCreate):
    def runTest(self):
        readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))
        p=Pipeline(name='juan', readset=readset)
        p.dict['readsfile']=readset['reads_file']
        p.load_steps() # no template pipeline/test.syml
        self.assertEqual(p.__class__,Pipeline)
        #print "TestLoad: pipeline is %s" % p


if __name__=='__main__':
    unittest.main()

