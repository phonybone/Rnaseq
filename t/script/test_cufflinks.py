import unittest, os, sys
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

dir=os.path.abspath(os.path.dirname(__file__)+"../common")
sys.path.append(dir)
from fragment_script import fragment_script, first_diff, diff_strs

class TestScript(unittest.TestCase):
    readset_file='paired1.syml'
    pipeline_name='cufflinks'
    
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        templated.template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/%s' % self.readset_file)[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

    def test_setup(self):
        self.assertEqual(self.pipeline.name, self.pipeline_name)

    def test_script(self):
        script_file=os.path.join(RnaseqGlobals.root_dir(),'t/fixtures/sh_scripts/cufflinks.s_1.sh')
        #f=open(script_file)
        #script=f.read()
        #close(f)
        #print "script is %d bytes" % len(script)

        expected=fragment_script(script_file)
        #for stepname, frag in expected.items():
            # print "expected(%s):\n%s" % (stepname, frag)
        #print "-=-=-=-======================================================"
        
        for step in self.pipeline.steps:
            if step.name=='header': continue
            step_script=step.sh_script(self.pipeline.context).strip()
            print "%s: first diff at %d" % (step.name, first_diff(step_script, expected[step.name]))
            print "%s diff: %s..." % (step.name, diff_strs(step_script, expected[step.name]))
            self.assertEqual(step_script, expected[step.name])

suite = unittest.TestLoader().loadTestsFromTestCase(TestScript)
unittest.TextTestRunner(verbosity=2).run(suite)


        

