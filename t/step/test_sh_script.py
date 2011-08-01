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

        script_file=os.path.join(RnaseqGlobals.root_dir(),'t','fixtures','sh_scripts','cufflinks.s_1.sh')
        self.script_fragments=fragment_script(script_file)

    def test_setup(self):
        self.assertEqual(len(self.script_fragments.keys()),12)


suite = unittest.TestLoader().loadTestsFromTestCase(TestShScript)
unittest.TextTestRunner(verbosity=2).run(suite)


