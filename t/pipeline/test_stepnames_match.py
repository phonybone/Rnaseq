import unittest, os, re
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))

class TestStepnames(TestBase):
    def test_stepnames(self):
        pipeline=Pipeline(name='juan', readset=self.readset).load_steps() # dying on badly configured i/o
        #print "pipeline.stepnames are %s" % pipeline.stepnames
        for stepname in pipeline.stepnames:
            self.assertTrue(isinstance(pipeline.stepWithName(stepname),Step))

    def test_missing_stepname(self):
        try: 
            pipeline=Pipeline(name='missing_stepname', readset=self.readset).load_steps()
            self.fail()
        except ConfigError as ce:
            self.assertTrue("The following steps were listed as part of missing_stepname, but no defining section was found: repeats_consensus", str(ce))
        except Exception as e:
            print "caught %s" % e
            self.fail()                 # getting here

    def test_extra_stepname(self):
        try: 
            pipeline=Pipeline(name='extra_stepname', readset=self.readset).load_steps()
        except Exception as e:
            print "e is %s" % e
            self.assertTrue(re.search("error loading step 'extra_step': No module named extra_step", str(e)))


        
suite = unittest.TestLoader().loadTestsFromTestCase(TestStepnames)
unittest.TextTestRunner(verbosity=2).run(suite)

