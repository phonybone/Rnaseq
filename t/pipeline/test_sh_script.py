import unittest, os, sys, yaml

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        RnaseqGlobals.set_conf_value('silent', True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        self.readset=Readset(reads_files=os.path.abspath(__file__+'/../../readset/s_?_export.txt'),
                             readlen=75,
                             working_dir='rnaseq_wf')
        self.pipeline=Pipeline(name='filter', readset=self.readset)

class TestListExpansion(TestInputs):
    def runTest(self):
        reads_path=self.readset.path_iterator()[0]
        self.readset['reads_file']=reads_path
        pipeline=Pipeline(name='filter', readset=self.readset)            
        pipeline.load_steps()
        script=pipeline.sh_script(force=True)
        #self.assertEqual(len(script),2987) # based on a test run; will squawk if anything changes
        mg=re.search('exit_on_failure',script)
        self.assertEqual(mg.group(0),'exit_on_failure') # this is from the header, should be only one
        try:
            mg.group(1)
            self.Fail()
        except Exception as e:
            self.assertEqual(str(e),'no such group')






#if __name__=='__main__':
#    unittest.main()

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestListExpansion)
unittest.TextTestRunner(verbosity=2).run(suite)
