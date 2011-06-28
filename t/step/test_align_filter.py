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


        rs_filename=os.path.abspath(os.path.dirname(__file__)+'/../fixtures/readsets/paired1.syml')
        self.readset=Readset.load(rs_filename)
        self.pipeline=Pipeline(name='filter', readset=self.readset)

    def test_sh_cmd(self):
        step=self.pipeline.stepWithName('remove_erccs')
        print step.sh_cmd()


suite = unittest.TestLoader().loadTestsFromTestCase(TestShScript)
unittest.TextTestRunner(verbosity=2).run(suite)


