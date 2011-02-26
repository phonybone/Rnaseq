import os, yaml, unittest


from superyaml import *
from warn import *

class TestSuperyaml(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_basic(self):
        sy=superyaml(domain=os.getcwd())
        
        d={'this':'that', 'these':'those'}
        d_sy=sy.load('basic.syml',d)
        self.assertEqual(d['this'],'that')
        self.assertEqual(d['these'],'those')

    def test_basic_substitution(self):
        sy=superyaml(domain=os.getcwd())
        d_sy=sy.load('basic_substitution.syml',{'these':'some other'})
        self.assertEqual(d_sy['these'],'some other')


    def test_internal_substitution(self):
        sy=superyaml(domain=os.getcwd())
        d_sy=sy.load('internal_substitution.syml',{'these':'some other'})
        self.assertEqual(d_sy['these'],'some other')
        self.assertEqual(d_sy['this_color'],'red', 'this_color=red: got %s' % d_sy['this_color'])
        
    def test_sections(self):
        sy=superyaml(domain=os.getcwd())
        d_sy=sy.load('sections.syml',{'these':'some other'})
        self.assertEqual(d_sy['these'],'some other')
        self.assertEqual(d_sy['this_color'],'red', 'this_color=red: got %s' % d_sy['this_color'])
        self.assertEqual(type(d_sy['section1']['flintstones']), type([]), "got a list for section1->flintstones")
        self.assertEqual(d_sy['section1']['flintstones'][0], 'fred', 'section1=fred: got %s' % d_sy['section1']['flintstones'][0])


if __name__=='__main__':
    unittest.main()                              # unittest.main(), actually
    
