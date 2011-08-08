import unittest, os, sys
sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestIsStepStep(unittest.TestCase):
    readset_file='paired1.syml'
    pipeline_name='bowtie'
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/%s' % self.readset_file)[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()
        self.step_factory=StepFactory()

    def test_setup(self):
        self.assertEqual(self.pipeline.name, self.pipeline_name)
        self.assertIsInstance(self.step_factory, StepFactory)

    def test_is_step(self):
        for stepname in ['bowtie', 'equalize', 'filterQuality', 'cufflinks', 'mapsplice']:
            #print "%s should be a step name" % stepname
            self.assertTrue(self.step_factory.is_step(stepname))
            
        for stepname in ['barf', 'moose', 'piglet', 'gandalf']:
            #print "%s should not be a step name" % stepname
            self.assertFalse(self.step_factory.is_step(stepname))
            
                        

suite = unittest.TestLoader().loadTestsFromTestCase(TestIsStepStep)
unittest.TextTestRunner(verbosity=2).run(suite)


        

