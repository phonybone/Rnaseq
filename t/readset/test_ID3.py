import unittest, os, sys, re

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))


from Rnaseq import *
from RnaseqGlobals import *
from warn import *


class TestID2(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/qiang_control.syml'
        self.rlist=Readset.load(readset_file)

    def test_setup(self):
        self.assertEqual(self.rlist[0].format, 'fq')

    def test_IDs(self):
        rs0=self.rlist[0]
        self.assertEqual(rs0.ID, os.path.join(rs0.reads_dir, rs0.working_dir, 'A172'))

        rs1=self.rlist[1]
        self.assertEqual(rs1.ID, os.path.join(rs1.reads_dir, rs1.working_dir, 'DBTRG'))

        rs2=self.rlist[2]
        self.assertEqual(rs2.ID, os.path.join(rs2.reads_dir, rs2.working_dir, 'SW1783'))




#        self.assertEqual(self.rlist[1].ID, 'DBTRG')
#        self.assertEqual(self.rlist[2].ID, 'SW1783')
        

suite = unittest.TestLoader().loadTestsFromTestCase(TestID2)
unittest.TextTestRunner(verbosity=2).run(suite)
    
