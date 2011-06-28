import unittest, os, re
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestMissingExe(unittest.TestCase):
    def test_missing_exe(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'), label='test_missing_exe').resolve_reads_file().resolve_working_dir().set_ID()
        pipeline=Pipeline(name='juan', readset=self.readset).load_steps() # dying on badly configured i/o

        fq_step=pipeline.stepWithName('filterQuality')
        self.assertTrue(isinstance(fq_step, Step))
        fq_step.exe='fred'
        self.assertFalse(fq_step.verify_exe())

suite = unittest.TestLoader().loadTestsFromTestCase(TestMissingExe)
unittest.TextTestRunner(verbosity=2).run(suite)
                        
