import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestSetup(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        self.readset=Readset(filename='../readset/readset.syml').load()
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        self.pipeline.load_steps()

class TestMergePipeline(TestSetup):
    def runTest(self):
        filename='user_config.yml'
        user_config=UserConfig().read(filename)

        self.assertEqual(type(user_config['pipeline_runs']),type([]))
        self.assertEqual(len(user_config['pipeline_runs']),2)
        pipeline_args=user_config['pipeline_runs'][0]

        pipeline=self.pipeline
        user_config.merge_args(pipeline,user_config['pipeline_runs'][0])
        self.assertEqual(pipeline.label, pipeline_args['label'])
        self.assertEqual(os.path.basename(pipeline.working_dir()), pipeline_args['working_dir'])

        self.assertEqual(pipeline_args['remove_erccs']['aligner'], 'blat')
        re_step=pipeline.stepWithName('remove_erccs')
        self.assertEqual(re_step.aligner(), 'blat')

        script=re_step.sh_cmd()
        mg=re.search('align_suffix=(\w+)',script)
        self.assertEqual(mg.group(1), 'fa')

        expected_script='''
align_suffix=fa
/proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/blat ERCC_reference_081215.2bit /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/user_config/rnaseq_wf/s_?_export.txt.riboMT_OK.fq -fastMap -q=DNA -t=DNA /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/user_config/rnaseq_wf/s_?_export.txt.blat_ercc_BAD.psl
#exit_on_failure $? remove_erccs
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/removeBlatHit.pl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/user_config/rnaseq_wf/s_?_export.txt.blat_ercc_BAD.psl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/user_config/rnaseq_wf/s_?_export.txt.riboMT_OK.fq > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/user_config/rnaseq_wf/s_?_export.txt.ercc_OK.fq
'''
        self.assertEqual(script,expected_script)


        print pipeline.sh_script()

if __name__=='__main__':
    unittest.main()

        
