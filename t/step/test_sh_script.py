import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        self.readset=Readset(name='readset').load()
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        RnaseqGlobals.set_conf_value(['rnaseq','aligner'],'blat')

class TestListExpansion(TestInputs):
    def runTest(self):
        reads_path=self.readset.path_iterator()[0]
        self.readset['reads_file']=reads_path
        pipeline=self.pipeline
        pipeline.load_steps()
        for step in pipeline.steps:
            print step.sh_cmd()






if __name__=='__main__':
    unittest.main()

