import unittest
from Rnaseq import *
from warn import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        pass

class TestGood(TestCreate):
    def runTest(self):
        warn("got here")
        readset=Readset(name='readset').load()
        p=Pipeline(name='test', readset=readset)
        print "p is %s" % p


class TestBad(TestCreate):
        readset=Readset(name='readset').load()
        try:
            p=Pipeline(name='test', readset=readset).load()
        except UserError as ue:
            print "caught %s" % ue
            

if __name__=='__main__':
    unittest.main()

