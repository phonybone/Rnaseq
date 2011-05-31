import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestSetup(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv


class TestReadConfig(TestSetup):
    def runTest(self):
        filename=os.path.abspath(os.path.dirname(__file__)+'/user_config.yml')
        user_config=UserConfig().read(filename)

        self.assertEqual(type(user_config['pipeline_runs']),type([]))
        self.assertEqual(len(user_config['pipeline_runs']),2)
        
        pipeline_args=user_config['pipeline_runs'][0]
        self.assertEqual(pipeline_args['pipeline'],'filter')
        self.assertEqual(pipeline_args['label'],'filter with blat')
        self.assertEqual(pipeline_args['remove_erccs']['aligner'],'blat')


if __name__=='__main__':
    unittest.main()

