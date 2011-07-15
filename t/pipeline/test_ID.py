import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

# OBSOLETE! ID functionality moved to readset

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__)

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/paired1.syml'
        self.readset=Readset.load(filename=readset_file)[0]

        try: del self.readset['working_dir']
        except KeyError: pass
        
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()
        try: del self.pipeline['working_dir']
        except KeyError: pass

        RnaseqGlobals.set_conf_value('wd_timestamp',False)

    def test_ID(self):
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

        

suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)

