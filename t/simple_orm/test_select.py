import unittest, os
from Rnaseq import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        self.db_file=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../fixtures/dbs/simple_orm.db"))
        self.sorm=SimpleOrm(db_file=self.db_file)

class TestSelect(TestBase):
    def runTest(self):
        sorm=self.sorm
        print "sorm is %s" % sorm


if __name__=='__main__':
    unittest.main()
        


