import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

from Rnaseq.steps.Header import *

class TestBase(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        RnaseqGlobals.set_conf_value('force',True)
        self.pipeline=Pipeline(name='filter')

class TestLoad(TestBase):
    def runTest(self):
        pipeline=self.pipeline
        pipeline.load_steps()

        self.assertEquals(len(pipeline.steps),4)
        
class TestShScript(TestBase):
    def runTest(self):
        pipeline=self.pipeline
        pipeline.load_steps()
        pipeline.readset=Readset(name='readset')
        script=pipeline.sh_script()
        print script

if __name__=='__main__':
    unittest.main()

