import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]


class TestBasicCreate(TestCreate):
    def runTest(self):
        readset=self.readset
        p=Pipeline(name='test', readset=readset)
        self.assertEqual(p.__class__,Pipeline)
        

class TestMissingTemplate(TestCreate):
    def runTest(self):
        with self.assertRaises(UserError):
            p=Pipeline(name='test', readset=self.readset).load() # no template pipeline/test.syml


class TestLoad(TestCreate):
    def runTest(self):
        readset=self.readset
        p=Pipeline(name='juan', readset=readset)
        p.dict['readsfile']=readset['reads_file']
        p.load_steps() # no template pipeline/test.syml
        self.assertEqual(p.__class__,Pipeline)
        #print "TestLoad: pipeline is %s" % p


suite = unittest.TestLoader().loadTestsFromTestCase(TestCreate)
unittest.TextTestRunner(verbosity=2).run(suite)


