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

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/paired2.syml'
        rlist=Readset.load(readset_file)
        self.readset=rlist[0]
        self.pipeline=Pipeline.get_pipeline(name='link', readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.readset.label, 's_1')
        self.assertEqual(self.pipeline.name, 'link')
        self.assertTrue(self.pipeline.context != None)

    def test_ID2(self):
        readset=self.readset
        self.assertEqual(len(readset.reads_files), 2)
        for rf in readset.reads_files:
            target_ID=readset.working_dir+'/'+os.path.basename(rf)
            target_ID=re.sub('_\d\..*$', '', target_ID)
            ID=readset.ID
            print "       ID: %s\ntarget ID: %s" % (ID, target_ID)
            self.assertEqual(ID, target_ID)


suite = unittest.TestLoader().loadTestsFromTestCase(TestID2)
unittest.TextTestRunner(verbosity=2).run(suite)
