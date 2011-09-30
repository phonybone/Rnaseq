import unittest, os, sys

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestMissingVar(unittest.TestCase):
    def test_missing_exe(self):
        RnaseqGlobals.initialize(__file__, testing=True)

        readset_file=RnaseqGlobals.root_dir()+"/t/fixtures/readsets/readset1.syml"
        self.readset=Readset.load(readset_file)[0]
        pipeline=Pipeline.get_pipeline(name='gene_expression', readset=self.readset).load_steps() # dying on badly configured i/o
        cl_step=pipeline.step_with_name('cufflinks')
        self.assertTrue(isinstance(cl_step, Step))

        del RnaseqGlobals.config['rnaseq']['ensembl_dir']

        try:
            sh_script=cl_step.sh_script(pipeline.context)
            self.fail("ConfigError should have been generated")
        except ConfigError as ce:
            self.assertRegexpMatches(str(ce), 'cufflinks')
            self.assertRegexpMatches(str(ce), 'EvalError')
            self.assertRegexpMatches(str(ce), 'ensembl_dir')


suite = unittest.TestLoader().loadTestsFromTestCase(TestMissingVar)
unittest.TextTestRunner(verbosity=2).run(suite)
                        
