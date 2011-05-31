import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestReport(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

    def runTest(self):
        step_run=StepRun(step_name='header', status='failed', successful=False, start_time=2, finish_time=5)
        expected='header                    '+"\t".join(['status: failed','success: failed','duration: 3 secs'])
        self.assertEqual(step_run.report(),expected)

if __name__=='__main__':
    unittest.main()

