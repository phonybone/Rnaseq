import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestSetup(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_?_export.txt'))


class TestWithPipeline(TestSetup):
    def runTest(self):
        filename=os.path.abspath(os.path.dirname(__file__)+'/user_config_juan.yml')
        user_config=UserConfig().read(filename)

        user_runs=user_config.user_runs()
        for user_run in user_runs:
            print "user_run['remove_erccs']['aligner'] is %s" % user_run['remove_erccs']['aligner']
            readset=self.readset
            for reads_path in readset.path_iterator():
                print "reads_path is %s" % reads_path
                readset['reads_file']=reads_path # this messes up the iterator
                pipeline=Pipeline(name='juan',readset=readset)
                pipeline.load_steps()
                user_config.merge_args(pipeline, user_run)
                step=pipeline.stepWithName('remove_erccs')
                self.assertEqual(step.aligner(), user_run['remove_erccs']['aligner'])
                print "got correct aligner %s" % step.aligner()

class TestWithoutPipeline(TestSetup):
    pass

if __name__=='__main__':
    unittest.main()

