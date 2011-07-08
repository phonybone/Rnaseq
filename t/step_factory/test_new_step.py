import unittest, os, sys, re

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *


class TestNewStep(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset1.syml'
        rlist=Readset.load(readset_file)
        self.readset=rlist[0]
        self.context=Context(readset)
        
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        self.factory=StepFactory(self.pipeline)

    def test_header(self):
        factory=self.factory
        header_step=factory.new_step('header')
        self.assertEqual(header_step.pipeline, self.pipeline)

        self.assertEqual(header_step.name, 'header')
        self.assertEqual(header_step.force, True)
        self.assertEqual(header_step.skip_success_check, True)

        readset=self.readset
        
        context={}
        script=header_step.sh_script(context)
        self.assertTrue(re.search('root_dir=%s' % RnaseqGlobals.root_dir(), script))
        self.assertTrue(re.search('programs=%s' % RnaseqGlobals.root_dir()+'/programs', script))
        self.assertTrue(re.search('reads_file=%s' % readset.reads_file, script))
        self.assertTrue(re.search('ID=%s' % readset.ID, script))
        self.assertTrue(re.search('working_dir=%s' % readset.working_dir, script))


    # test the fq_all2std step because it's the next simplest step type after header:
    # takes one input, writes one output
    def test_export2fq(self):
        e2f_step=self.factory.new_step('export2fq')
        self.assertEqual(e2f_step.name, 'export2fq')
        print "class is",e2f_step.__class__
        self.assertEqual(e2f_step.__class__.__name__, 'export2fq')

        script=e2f_step.sh_script({'inputs':['/some/input/data.txt']})
        print "e2f script:\n%s" % script

    def test_align_filter(self):
        af_step=self.factory.new_step('align_filter', aligner='bowtie')
        self.assertEqual(af_step.aligner, 'bowtie')
        

suite = unittest.TestLoader().loadTestsFromTestCase(TestNewStep)
unittest.TextTestRunner(verbosity=2).run(suite)
