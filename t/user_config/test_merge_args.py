import unittest, os, sys

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
        self.assertTrue(re_step.aligner, 'blat')

        print re_step.sh_cmd()
        #print yaml.dump(pipeline)
        

if __name__=='__main__':
    unittest.main()

        
