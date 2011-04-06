import unittest
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
        print "evd is %s" % evd

        self.assertEqual(evd['fred'],'${fred}')
        
        self.assertEqual(evd['this'],'that')
        self.assertEqual(evd['these'],'those')
        
        self.assertEqual(evd.this, 'that')
        self.assertEqual(evd.these, 'those')

        print "TestCreate done"


class TestUpdate(TestBase):
    def runTest(self):
        evd=evoque_dict(this='that', these='those')
        d={'honda':'red', 'yamaha':'blue'}
        evd.update(d)

        try:
            print "1. evd.honda=%s (yay)" % evd.honda
        except AttributeError as ae:
            print "1. ae=%s" % ae

        try:
            self.assertEqual(evd['honda'],'red')
        except IndexError as ie:
            print "2. ie=%s" % ie



        self.assertEqual(evd['honda'], 'red')
        self.assertEqual(evd['yamaha'],'blue')
        print "TestUpdate done"

if __name__=='__main__':
    unittest.main()

