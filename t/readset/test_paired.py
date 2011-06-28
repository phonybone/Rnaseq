import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
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
        rs_filename=os.path.abspath(os.path.dirname(__file__)+'../fixtures/readsets/paired1.syml')
        rlist=Readset.load(rs_filename)
        self.assertEqual(len(rlist),2)

        rs=rlist[0]
        self.assertEqual(rs.org, 'human')
        self.assertEqual(rs.readlen,101)
        self.assertEqual(rs.reads_dir ,'/proj/hoodlab/share/vcassen/rna-seq/qiang_data')
        self.assertEqual(rs.working_dir ,'/proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq')
        self.assertEqual(rs.format ,'fq')
        self.assertEqual(rs.paired_reads ,True)
        self.assertEqual(rs.reads_file ,'/proj/hoodlab/share/vcassen/rna-seq/qiang_data/s_1_1_sequence.txt')
        self.assertEqual(rs.ID ,'/proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1')
        self.assertEqual(rs.label ,'s_1_1')
        self.assertEqual(rs.description ,'s_1_1')


suite = unittest.TestLoader().loadTestsFromTestCase(TestPaired)
unittest.TextTestRunner(verbosity=2).run(suite)


