import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestReport(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv

    def runTest(self):
        # all this is really testing is that there is a pipeline_run object in the test database
        session=RnaseqGlobals.get_session()
        pipeline_run=session.query(PipelineRun).first()
        self.assertEqual(pipeline_run.__class__, PipelineRun)
        #print pipeline_run.report()
        


if __name__=='__main__':
    unittest.main()

