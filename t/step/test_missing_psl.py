import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, opt_list=['--aligner','blat'])       # not to be confused with sys.argv
        template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),RnaseqGlobals.conf_value('testing','template_dir'))
        templated.template_dir=template_dir

        self.readset=Readset(reads_files=os.path.abspath(__file__+'/../../readset/s_?_export.txt'),
                             readlen=75,
                             working_dir='rnaseq_wf')
        
        self.pipeline=Pipeline(name='missing psl', readset=self.readset)
        

class TestMissingStep(TestInputs):
    def runTest(self):
        try:
            self.pipeline.load_steps()
            self.fail()
        except ConfigError as ce:
            self.assertTrue(re.search('No module named missing_psl', str(ce)))
        except Exception as e:
            self.fail("Didn't raise config error for missing step as expected (raised %s instead)" % e)

class TestListExpansion(TestInputs):
    def runTest(self):
        step=self.pipeline.stepWithName('missing_psl')
        self.assertEqual(step,None)



suite = unittest.TestLoader().loadTestsFromTestCase(TestInputs)
unittest.TextTestRunner(verbosity=2).run(suite)

