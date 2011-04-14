import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__)

class TestDict(TestCreate):
    def runTest(self):
        readset=Readset(filename='readset.syml').load()
        self.assertEqual(readset.filename, 'readset.syml')

        self.assertEqual(readset['reads_file'],'s_?_export.txt')
        self.assertEqual(readset['description'],'this is a sample readset')
        self.assertEqual(readset['org'],'mouse')
        self.assertEqual(readset['readlen'],75)
        self.assertEqual(readset['working_dir'],'rnaseq_wf')
        

        vars={'this': 'that'}
        readset.update(vars)
        self.assertEqual(readset['this'],'that')
        
        print "TestDict passed"


if __name__=='__main__':
    unittest.main()

        
        
