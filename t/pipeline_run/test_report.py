import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestReport(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__)       # not to be confused with sys.argv

    def runTest(self):
        session=RnaseqGlobals.get_session()
        pipeline_run=session.query(PipelineRun).filter_by(id=1).first()
        print pipeline_run.report()
        


if __name__=='__main__':
    unittest.main()

