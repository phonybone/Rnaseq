import unittest, os
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)

class TestPathIterator(TestCreate):
    def runTest(self):
        readset=Readset(reads_files=os.path.abspath(os.path.dirname(__file__)+'/s_?_export.txt'))
        path_it=readset.path_iterator()
        self.assertEqual(len(path_it),3)

class TestPathIterator2(TestCreate):
    def runTest(self):
        readset=Readset(reads_files=os.path.abspath(os.path.dirname(__file__)+'/s_?_export.txt'))
        
        path_it=readset.path_iterator()
        self.assertEqual(len(path_it),3)

        # do it twice:
        path_it2=readset.path_iterator()
        self.assertEqual(len(path_it2),3)
        self.assertListEqual(path_it, path_it2)

class TestWhileLoop(TestCreate):
    def runTest(self):
        readset=Readset(reads_files=os.path.abspath(os.path.dirname(__file__)+'/s_?_export.txt'))
        i=0
        while True:
            readsfile=readset.next_reads_file()
            if readsfile==None: break
            i+=1
        self.assertEqual(i,3)



if __name__=='__main__':
    unittest.main()

