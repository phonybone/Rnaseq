import unittest, os, sys, yaml

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_?_export.txt'))

class TestListExpansion(TestInputs):
    def runTest(self):
        
        for reads_path in self.readset.path_iterator():
            self.readset['reads_file']=reads_path

            pipeline=Pipeline(name='filter', readset=self.readset)
            pipeline.load_steps()
            step=pipeline.stepWithName('export2fq')

            self.assertTrue(isinstance(step, Step))
            self.assertIn(self.readset['reads_file'],step.inputs())
            self.assertIn("%s.fq" % self.readset['reads_file'], step.outputs())



suite = unittest.TestLoader().loadTestsFromTestCase(TestListExpansion)
unittest.TextTestRunner(verbosity=2).run(suite)

