import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__)
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))
        try: del self.readset['working_dir']
        except KeyError: pass
        
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()
        try: del self.pipeline['working_dir']
        except KeyError: pass

        RnaseqGlobals.set_conf_value('wd_timestamp',False)

class TestCreate(TestBase):

    def runTest(self):
        readset=self.readset
        pipeline=self.pipeline

        # no working dir set anywhere (as per setup):
        self.assertEqual(pipeline.ID(), readset['reads_file'])

        # working_dir set in readset (not timestamp)
        readset['working_dir']='rnaseq_wf'
        self.assertEqual(pipeline.ID(), os.path.join(os.path.dirname(readset['reads_file']), readset['working_dir'],os.path.basename(readset['reads_file'])))
        
        # working_dir set in readset (timestamp)
        del readset['working_dir']
        readset['working_dir']='wd_timestamp'
        wd=pipeline.ID()
        self.assertTrue(re.match('rnaseq_\d\d\w\w\w\d\d.\d\d\d\d\d\d', os.path.basename(os.path.dirname(wd))))


        # working_dir set in pipeline:
        pipeline['working_dir']='rnaseq_wd'
        del readset['working_dir']
        self.assertEqual(pipeline.ID(), os.path.join(os.path.dirname(readset['reads_file']), pipeline['working_dir'],os.path.basename(readset['reads_file'])))

        # relative wd and relative reads file:
        pipeline['working_dir']='pipeline_wd'
        readset['reads_file']='relative.pathname'
        self.assertEqual(pipeline.ID(), os.path.join(os.getcwd(), 'pipeline_wd', os.path.basename(readset['reads_file'])))

        

if __name__=='__main__':
    unittest.main()

