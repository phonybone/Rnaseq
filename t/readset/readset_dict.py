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
        readset=Readset(name='readset').load(vars=RnaseqGlobals.config)
        self.assertEqual(readset.name, 'readset')

        print "%s" % readset.dict
        self.assertEqual(type(readset.dict),type({}))
        self.assertEqual(readset.dict['name'],'readset')
        self.assertEqual(readset.name, 'readset')

        vars={'this': 'that'}
        readset.dict.update(vars)
        self.assertEqual(readset.dict['this'],'that')
        
        print "TestDict passed"


if __name__=='__main__':
    unittest.main()

        
        
