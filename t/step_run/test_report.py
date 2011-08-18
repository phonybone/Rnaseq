import unittest, os, sys


dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestReport(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

    def runTest(self):
        step_run=StepRun(step_name='header', status='failed', successful=False, start_time=2, finish_time=5)
        expected='header                    '+"\t".join(['status: failed','success: failed','duration: 3 secs','id: None'])
        self.assertEqual(step_run.report(),expected)

if __name__=='__main__':
    unittest.main()

