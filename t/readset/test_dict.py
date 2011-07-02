import unittest, os
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

# tests the dictionary-attribute equivalence of readsets

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)

class TestDict(TestCreate):
    def test_dict(self):
        dir=RnaseqGlobals.root_dir()+'/t/fixtures/readsets'
        os.chdir(dir)
        filename=os.path.join(dir,'readset_rel_glob.syml')
        rlist=Readset.load(filename)
        readset=rlist[0]
        
        self.assertRegexpMatches(readset['reads_file'], dir+'/s_\d_export.txt')
        self.assertEqual(readset['description'],'this is a sample readset (fixture)')
        self.assertEqual(readset['org'],'mouse')
        self.assertEqual(readset['readlen'],75)
        self.assertEqual(readset['working_dir'],'rnaseq_wf')
        

        vars={'this': 'that'}
        readset.update(vars)
        self.assertEqual(readset['this'],'that')
        


suite = unittest.TestLoader().loadTestsFromTestCase(TestDict)
unittest.TextTestRunner(verbosity=2).run(suite)


        
        
