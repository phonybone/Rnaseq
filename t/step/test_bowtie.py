import unittest, sys, os
dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestBowtieStep(unittest.TestCase):
    readset_file='paired1.syml'
    pipeline_name='bowtie'
    
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
    def test_bowtie_step_single(self):
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml')[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

        bowtie_step=self.pipeline.step_with_name('bowtie')
        script=bowtie_step.sh_script(self.pipeline.context)
        #print "script:\n>>>%s<<<" % script
        output=bowtie_step.output_list()[0]

        expected='''
export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie --sam --threads 4 --quiet -k 1 -v 2 -q hg19 -1 /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/rnaseq/s_1_2_sequence.fq %s
        ''' % output
        #print "expected:\n>>>%s<<<" % expected


    def test_bowtie_step_paired(self):
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/paired1.syml')[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

        bowtie_step=self.pipeline.step_with_name('bowtie')
        script=bowtie_step.sh_script(self.pipeline.context)
        output=bowtie_step.output_list()[0]
        
        expected='''
export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie --sam --threads 4 --quiet -k 1 -v 2 -q hg19 -1 /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/rnaseq/s_1_1_sequence.fq -2 /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/readsets/rnaseq/s_1_2_sequence.fq %s
''' % output
        #print "script:\n>>>%s<<<" % script
        #print "expected:\n>>>%s<<<" % expected
        self.assertEqual(script.strip(),expected.strip())


suite = unittest.TestLoader().loadTestsFromTestCase(TestBowtieStep)
unittest.TextTestRunner(verbosity=2).run(suite)


        

