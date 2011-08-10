import unittest, os, sys, re


dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *

# Tests the addition of paired end fields with a readset (these are not explicitly mentioned in readset.py)

class TestPaired(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir

    def test_load(self):
        rs_filename=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/paired1.syml'
        rlist=Readset.load(rs_filename)
        self.assertEqual(len(rlist),1)

        rs=rlist[0]
        self.assertEqual(rs.org, 'human')
        self.assertEqual(rs.readlen,101)
        self.assertEqual(rs.reads_dir , RnaseqGlobals.root_dir()+'/t/fixtures/readsets')
        self.assertEqual(rs.working_dir ,'/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/rnaseq')
        self.assertEqual(rs.format ,'fq')
        self.assertEqual(rs.paired_end ,True)
        self.assertEqual(rs.reads_files[0] ,'/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/s_1_1_sequence.txt')
        self.assertEqual(rs.reads_files[1] ,'/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/s_1_2_sequence.txt')
        self.assertEqual(rs.ID ,'/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/rnaseq/s_1')
        self.assertEqual(rs.label ,'s_1')
        self.assertEqual(rs.description ,'s_1')


suite = unittest.TestLoader().loadTestsFromTestCase(TestPaired)
unittest.TextTestRunner(verbosity=2).run(suite)


