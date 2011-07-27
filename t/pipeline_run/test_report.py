import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestPipelineRunReport(unittest.TestCase):
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir

        session=RnaseqGlobals.get_session()
        for sr in session.query(StepRun).all():
            session.delete(sr)
        for pr in session.query(PipelineRun).all():
            session.delete(pr)
        session.commit()

    def test_setup(self):
        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        self.assertTrue(len(prs)==0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestPipelineRunReport)
unittest.TextTestRunner(verbosity=2).run(suite)

