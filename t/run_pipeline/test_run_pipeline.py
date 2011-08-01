import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestRunPipeline(unittest.TestCase):
    readset_file=os.path.abspath(os.path.dirname(__file__)+'../fixtures/readsets/readset1.syml')
    pipeline_name='filter'
    
    
    def setUp(self):
        self.argv=RnaseqGlobals.initialize(__file__, testing=True, opt_list=['run', '-n', '-r', self.readset_file, '-p', self.pipeline_name])
      
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
    def test_run_pipeline(self):
        # create the Command object and run it:
        cf=CmdFactory(program='rnaseq')
        cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
        cmd=cf.new_cmd('run')
        cmd.run(self.argv, config=RnaseqGlobals.config)
        
        # confirm the existance of the pipeline's script:
        for rs in cmd.readsets:
            pipeline=cmd.pipelines[id(rs)]
            script_file=pipeline.scriptname()
            print "script_file is %s" % script_file
            self.assertTrue(os.path.isfile(script_file))
            mod_time=os.stat(script_file).st_mtime
            now=time.time()
            self.assertTrue(now > mod_time)
            self.assertTrue(now-mod_time < 10) # script_file created in the last 10 seconds?
                            
            # make sure we didn't miss any variables:
            f=open(script_file)
            script=f.read()
            f.close()
            self.assertNotRegexpMatches(script, 'built-in')

        # confirm the existance of the pipeline's output(s): (except that we didn't run it; see '-n' in opt_list, above)


suite = unittest.TestLoader().loadTestsFromTestCase(TestRunPipeline)
unittest.TextTestRunner(verbosity=2).run(suite)


        

