import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestShScript(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir


        readset_file=RnaseqGlobals.root_dir()+"/t/fixtures/readsets/paired1.syml"
        self.readset=Readset.load(readset_file)[0]
        self.pipeline=Pipeline(name='filter', readset=self.readset).load_steps()

    def test_sh_cmd(self):
        step=self.pipeline.step_with_name('remove_erccs')
        self.assertNotEqual(step, None)


        try:
            script=step.sh_script(self.pipeline.context)
        except Exception as e:
            print "test_align_filter: caught %s (%s)" % (e, type(e))
            self.fail()

        expected='''

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie ERCC_reference_081215 --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q ${ID} | perl -lane 'print unless($F[1] == 4)' > /proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1.remove_erccs_BAD.fq
'''
        self.assertEqual(script,expected)


suite = unittest.TestLoader().loadTestsFromTestCase(TestShScript)
unittest.TextTestRunner(verbosity=2).run(suite)


