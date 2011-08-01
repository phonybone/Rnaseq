import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    readset_name='readset1.syml'
    pipeline_name='cufflinks'
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/'+self.readset_name)[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.readset.name, self.readset_name)
        self.assertEqual(self.pipeline.name, self.pipeline_name)

    def test_input_conversion(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


        

