import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../common"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

from fragment_script import *

# Test step.

class TestShScript(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir


        reads_file=reads_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml'
        self.readset=Readset.load(reads_file)[0]
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        RnaseqGlobals.set_conf_value(['rnaseq','aligner'],'blat')

        self.script_fragments=fragment_script('cufflinks.s_1.sh')

    def test_setup(self):
        self.assertEqual(len(self.script_fragments.keys()),12)
        print self.script_fragments.keys()


    
    # look for presence of "${}" constructs in pipeline's sh_script()
    # obsolete: pipeline will legitimately have ${} scattered throughout.
    def old_test_sh_script(self):
        reads_path=self.readset.reads_file
        pipeline=self.pipeline
        pipeline.load_steps()
        for step in pipeline.steps:
            if step.name == 'header': continue # header legitimately has ${} constructs
            cmd=step.sh_cmd()
            mg=re.search('\$\{.*\}',cmd)
            if mg != None:
                print "%s: found ${} in %s" % (step.name, cmd)
                self.fail()



suite = unittest.TestLoader().loadTestsFromTestCase(TestShScript)
unittest.TextTestRunner(verbosity=2).run(suite)


