import unittest, re
from Rnaseq import *
from RnaseqGlobals import *
from warn import *
from evoque_dict import evoque_dict
import yaml

class TestBase(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__)

class TestCreate(TestBase):
    def runTest(self):
        evd=evoque_dict(this='that', these='those')

        self.assertEqual(evd['fred'],'${fred}')
        
        self.assertEqual(evd['this'],'that')
        self.assertEqual(evd['these'],'those')
        
        self.assertEqual(evd.this, 'that')
        self.assertEqual(evd.these, 'those')


class TestUpdate(TestBase):
    def runTest(self):
        evd=evoque_dict(this='that', these='those')
        d={'honda':'red', 'yamaha':'blue'}
        evd.update(d)

        try:
            print "1. evd.honda=%s (yay)" % evd.honda
            self.fail()
        except AttributeError as ae:
            self.assertTrue(re.search("object has no attribute 'honda'", str(ae)))

        try:
            self.assertEqual(evd['honda'],'red')
        except IndexError as ie:
            self.fail()



        self.assertEqual(evd['honda'], 'red')
        self.assertEqual(evd['yamaha'],'blue')

if __name__=='__main__':
    unittest.main()

