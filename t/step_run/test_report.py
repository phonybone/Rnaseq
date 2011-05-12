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
        step_run=session.query(StepRun).filter_by(id=4).first()
        print "step_run is %s" % step_run
        print "report is %s" % step_run.report()


if __name__=='__main__':
    unittest.main()

