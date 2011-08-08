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
        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/paired1.syml'
        self.readset=Readset.load(filename=readset_file)[0]
        
        self.pipeline=Pipeline(name='test_newstep', readset=self.readset)

    def test_new_step(self):
        pipeline=self.pipeline
        step_factory=StepFactory()
        step=step_factory.new_step(pipeline, 'Header',name='some name',arbitrary='giraffe')
        self.assertEqual(step.__class__, Header)
        self.assertEqual(step.name,'some name')
        self.assertEqual(step.arbitrary, 'giraffe')
        


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)

