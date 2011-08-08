import unittest, os, re
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        templated.template_dir=RnaseqGlobals.root_dir()+"/t/fixtures/templates"
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]

class TestStepnames(TestBase):
    def atest_stepnames(self):
        pipeline=Pipeline(name='juan', readset=self.readset).load_steps() # dying on badly configured i/o
        for stepname in pipeline.stepnames:
            self.assertTrue(isinstance(pipeline.step_with_name(stepname),Step))

    def test_missing_stepname(self):
        try: 
            pipeline=Pipeline(name='missing_stepname', readset=self.readset).load_steps()
            self.fail()
        except ConfigError as ce:
            self.assertRegexpMatches(str(ce), 'not listed: repeats_consensus$')
        except Exception as e:
            #print "caught %s (%s)" % (e, type(e))
            self.fail()                 # getting here

    def atest_extra_stepname(self):
        try: 
            pipeline=Pipeline(name='extra_stepname', readset=self.readset).load_steps()
        except Exception as e:
            # print "e is %s" % e
            self.assertTrue(re.search("error loading step 'extra_step': No module named extra_step", str(e)))


        
suite = unittest.TestLoader().loadTestsFromTestCase(TestStepnames)
unittest.TextTestRunner(verbosity=2).run(suite)

