import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

from Rnaseq.steps.Header import *

class TestBase(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)
        self.pipeline=Pipeline(name='test_newstep')

class TestNewStep(TestBase):
    def runTest(self):
        pipeline=self.pipeline
        step=pipeline.new_step('Header',name='some name',arbitrary='giraffe')
        self.assertEqual(step.__class__, Header)
        self.assertEqual(step.name,'some name')
        self.assertEqual(step.arbitrary, 'giraffe')
        


if __name__=='__main__':
    unittest.main()

