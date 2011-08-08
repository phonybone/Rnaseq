import unittest, os, re
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestUnknownStep(unittest.TestCase):
    def test_unknown_exe(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]
        pipeline=Pipeline(name='juan', readset=self.readset).load_steps() # dying on badly configured i/o

        try:
            step_factory=StepFactory()
            unknown_step=step_factory.new_step(pipeline, 'unknown')
            self.fail()
        except ConfigError as ce:
            self.assertTrue(re.search("error loading step 'unknown'", str(ce)))

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestUnknownStep)
unittest.TextTestRunner(verbosity=2).run(suite)
