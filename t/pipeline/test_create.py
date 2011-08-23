import unittest, sys, os

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]


    def test_basic_create(self):
        readset=self.readset
        p=Pipeline(name='test', readset=readset)
        self.assertEqual(p.__class__,Pipeline)
        

    def test_missing_template(self):
        with self.assertRaises(UserError):
            p=Pipeline(name='test', readset=self.readset).load() # no template pipeline/test.syml


    def test_load(self):
        readset=self.readset
        p=Pipeline(name='juan', readset=readset)
        p.dict['readsfile']=readset['reads_file']
        p.load_steps() # no template pipeline/test.syml
        self.assertEqual(p.__class__,Pipeline)
        #print "TestLoad: pipeline is %s" % p


suite = unittest.TestLoader().loadTestsFromTestCase(TestCreate)
unittest.TextTestRunner(verbosity=2).run(suite)


