import unittest, os, sys

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        template_dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../fixtures/templates")
        templated.template_dir=template_dir
        self.readset=Readset(name='readset').load()
        self.pipeline=Pipeline(name='filter', readset=self.readset)
        self.pipeline.load()

class TestListExpansion(TestInputs):
    def runTest(self):
        step=self.pipeline.stepWithName('export2fq')
        self.assertEqual(step.__class__, Step)
        self.assertEqual(step.inputs()[0], self.readset.reads_file)
        self.assertEqual(step.outputs()[0], "%s.fq" % self.readset.reads_file)


if __name__=='__main__':
    unittest.main()

