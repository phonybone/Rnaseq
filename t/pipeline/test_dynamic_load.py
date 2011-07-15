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
        RnaseqGlobals.set_conf_value('silent',True)
        readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]
        self.pipeline=Pipeline(name='filter', readset=readset)


class TestLoad(TestBase):
    def runTest(self):
        pipeline=self.pipeline
        pipeline.load_steps()

        self.assertEquals(len(pipeline.steps),6)
        
class TestShScript(TestBase):
    def runTest(self):
        pipeline=self.pipeline
        pipeline.load_steps()
        script=pipeline.sh_script()
        mg=re.search('exit_on_failure',script)
        self.assertEqual(mg.group(0),'exit_on_failure') # this is from the header, should be only one
        try:
            mg.group(1)
            self.Fail()
        except Exception as e:
            self.assertEqual(str(e),'no such group')


suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


