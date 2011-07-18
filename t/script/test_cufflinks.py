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

    # test each step fragment:
    def test_step_scripts(self):
        script_file=os.path.join(RnaseqGlobals.root_dir(),'t/fixtures/sh_scripts/cufflinks.sh')
        expected=fragment_script(script_file)
        
        for step in self.pipeline.steps:
            if step.name=='header': continue
            step_script=step.sh_script(self.pipeline.context, echo_name=True).strip()
            
            fd=first_diff(step_script, expected[step.name])
            if fd >= 0:
                print "%s: first diff at %d" % (step.name, fd)
                (d1,d2)=diff_strs(step_script, expected[step.name])
                print "%s diff:\ngenerated: %s\nexpected:  %s" % (step.name, d1, d2)
            self.assertEqual(step_script, expected[step.name])

    # generate the script and store it to disk:
    # (remove leading 'o_' to run; see docs on unittest for details)
    def o_test_pipeline_script(self):
        script=self.pipeline.sh_script()
        f=open('cufflinks.sh','w')
        f.write(script)
        f.close()
        print "'cufflinks.sh' written"
        

suite = unittest.TestLoader().loadTestsFromTestCase(TestScript)
unittest.TextTestRunner(verbosity=2).run(suite)


        

