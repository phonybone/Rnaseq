import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *


class TestShScript(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml'
        rlist=Readset.load(readset_file)
        self.readset=rlist[0]

    def test_header_script(self):

        
