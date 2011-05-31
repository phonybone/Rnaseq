import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestSetup(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        RnaseqGlobals.set_conf_value('silent',True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'))

        self.pipeline=Pipeline(name='filter', readset=self.readset)
        self.pipeline.load_steps()

class TestMergePipeline(TestSetup):
    def runTest(self):
        filename=os.path.abspath(os.path.dirname(__file__)+'/user_config.yml')
        user_config=UserConfig().read(filename)

        # check that we read in a list of merge-blocks under 'pipeline_runs':
        self.assertEqual(type(user_config['pipeline_runs']),type([]))
        self.assertEqual(len(user_config['pipeline_runs']),2)
        pipeline_args=user_config['pipeline_runs'][0]

        # merge the merge-block into the pipeline, and see if the merges take:
        pipeline=self.pipeline
        user_config.merge_args(pipeline,user_config['pipeline_runs'][0])
        self.assertEqual(pipeline.label, pipeline_args['label'])
        self.assertEqual(os.path.basename(pipeline.working_dir()), pipeline_args['working_dir'])

        # Check to see that a step parameter takes:
        self.assertEqual(pipeline_args['remove_erccs']['aligner'], 'blat')
        re_step=pipeline.stepWithName('remove_erccs')
        self.assertEqual(re_step.aligner(), 'blat')

        # Generate the step's sh_script, and see if it matches the expected (fixme: fragile test)
        script=re_step.sh_cmd()
        mg=re.search('align_suffix=(\w+)',script)
        self.assertEqual(mg.group(1), 'fa')
        self.assertTrue(re.search('programs/blat',script))
        self.assertTrue(re.search('ERCC_reference_081215.2bit', script))
        self.assertFalse(re.search('ERCC_reference_081215 ', script)) # bowtie ref, no '2bit'
        
        expected_script='''
align_suffix=fa
/proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/blat ERCC_reference_081215.2bit /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.riboMT_OK.fq -fastMap -q=DNA -t=DNA /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.blat_ercc_BAD.psl
#exit_on_failure $? remove_erccs
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/removeBlatHit.pl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.blat_ercc_BAD.psl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.riboMT_OK.fq > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.ercc_OK.fq
'''
        

        self.assertEqual(len(script),len(expected_script))

        
        script=pipeline.sh_script()
        expected_script='''#!/bin/sh

# header
echo step header 1>&2
# header
echo
echo '****************************************************************'
echo starting filter
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting filter
date 1>&2
echo 1>&2

export PATH=/tools/bin:/hpc/bin:/bin:/usr/bin/
export PYTHONPATH=${PYTHONPATH}:/proj/hoodlab/share/vcassen/rna-seq/rnaseq/lib

exit_on_failure()
{
  retcode=$1
  pipelinerun_id=$2
  step_id=$3
  next_step_id=$4

  python /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/provenance mid_step ${pipelinerun_id} ${step_id} ${next_step_id} ${retcode}
  

  if [ $retcode != 0 ]; then
    echo ${last_step} failed 1>&2
    exit $retcode
  else
    echo ${last_step} passed 1>&2
  fi
}



# export2fq
echo step export2fq 1>&2
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/fq_all2std.pl solexa2fastq /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.fq

# filterQuality
echo step filterQuality 1>&2
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/filterQuality.pl -v -i /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.fq -o /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.qual_OK.fq -b /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.bowtie_qual_BAD.fq

# filterLowComplex
echo step filterLowComplex 1>&2
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/filterLowComplex.pl -v -i /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.qual_OK.fq -o /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.complex_OK.fq -b /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.bowtie_complex_BAD.fq

# ribosomal_mit
echo step ribosomal_mit 1>&2
export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
/proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/bowtie human.GRCh37.61.rRNA-MT --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q --un /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.riboMT_OK.fq /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.complex_OK.fq | perl -lane 'print unless($F[1] == 4)' > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.bowtie_riboMT_BAD.sam
# remove_erccs
echo step remove_erccs 1>&2
align_suffix=fa
/proj/hoodlab/share/vcassen/rna-seq/rnaseq/programs/blat ERCC_reference_081215.2bit /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.riboMT_OK.fq -fastMap -q=DNA -t=DNA /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.blat_ercc_BAD.psl
#exit_on_failure $? remove_erccs
perl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/removeBlatHit.pl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.blat_ercc_BAD.psl /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.riboMT_OK.fq > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/readset/s_1_export.txt.ercc_OK.fq

'''

        #i=2000
        #print "script is %s" % script[0:i]
        #self.assertEqual(script[0:i],expected_script[0:i])
        #self.assertEqual(len(script),len(expected_script))

if __name__=='__main__':
    unittest.main()

        
