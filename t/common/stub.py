import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]
        self.pipeline=Pipeline(name='cufflinks', readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.readset.name, 'test_readset')


    def test_input_conversion(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


        

