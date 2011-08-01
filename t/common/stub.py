import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBowtieStep(unittest.TestCase):
    readset_file='paired1.syml'
    pipeline_name='bowtie'
    
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/%s' % self.readset_file)[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.pipeline.name, self.pipeline_name)


    def test_input_conversion(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestBowtieStep)
unittest.TextTestRunner(verbosity=2).run(suite)


        

