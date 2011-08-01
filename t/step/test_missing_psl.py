import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestMissingPsl(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        # argv=RnaseqGlobals.initialize(__file__, testing=True, opt_list=['--aligner','blat'])       # not to be confused with sys.argv
        template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),RnaseqGlobals.conf_value('testing','template_dir'))
        templated.template_dir=template_dir

        readset_file=RnaseqGlobals.root_dir()+"/t/fixtures/readsets/readset1.syml"
        self.readset=Readset.load(readset_file)[0]
        
        self.pipeline=Pipeline(name='missing psl', readset=self.readset)
        

    def test_missing_step(self):
        try:
            self.pipeline.load_steps()
            self.fail()
        except ConfigError as ce:
            self.assertTrue(re.search('No module named missing_psl', str(ce)))
        except Exception as e:
            self.fail("Didn't raise config error for missing step as expected (raised %s instead)" % e)

    def test_list_expansion(self):
        step=self.pipeline.step_with_name('missing_psl')
        self.assertEqual(step,None)



suite = unittest.TestLoader().loadTestsFromTestCase(TestMissingPsl)
unittest.TextTestRunner(verbosity=2).run(suite)

