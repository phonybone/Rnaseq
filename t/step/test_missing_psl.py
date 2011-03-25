import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, opt_list=['--aligner','blat'])       # not to be confused with sys.argv
        template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),RnaseqGlobals.conf_value('testing','template_dir'))
        templated.template_dir=template_dir

        self.readset=Readset(name='readset').load(vars=RnaseqGlobals.config)
        self.pipeline=Pipeline(name='missing psl', readset=self.readset)
        self.pipeline.load()
        

    
class TestListExpansion(TestInputs):
    def runTest(self):
        step=self.pipeline.stepWithName('missing_psl')
        with self.assertRaises(ConfigError) as ce:
            step.sh_cmd()

        print "ce is %s" % ce
        #self.assertEqual(ce



if __name__=='__main__':
    unittest.main()

