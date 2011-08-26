import unittest, os, sys, re

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))


from Rnaseq import *
from RnaseqGlobals import *
from warn import *


class TestID1(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml'
        rlist=Readset.load(readset_file)
        self.readset=rlist[0]
        self.pipeline=Pipeline.get_pipeline(name='link', readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.readset.name, 'readset1.syml')
        self.assertEqual(self.pipeline.name, 'link')
        self.assertTrue(self.pipeline.context != None)
        
    def test_ID(self):
        readset=self.readset
        header_step=self.pipeline.step_with_name('header')
        script=header_step.sh_script(self.pipeline.context)
        self.assertEqual(len(readset.reads_files), 1)
        rf=readset.reads_files[0]
        target_ID=readset.working_dir+'/'+os.path.basename(rf)
        target_ID=re.sub('\..*$', '', target_ID)
        ID=readset.ID
        self.assertEqual(ID, target_ID)
        #print "%s=\n%s" % (ID, target_ID)

suite = unittest.TestLoader().loadTestsFromTestCase(TestID1)
unittest.TextTestRunner(verbosity=2).run(suite)
