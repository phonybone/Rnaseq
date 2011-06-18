import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestShScript(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir


        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'), label='test_missing_exe').resolve_reads_file().resolve_working_dir().set_ID()
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        RnaseqGlobals.set_conf_value(['rnaseq','aligner'],'blat')

    def test_sh_script(self):
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


