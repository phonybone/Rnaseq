import unittest, os
from Rnaseq import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        self.db_file=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../fixtures/dbs/simple_orm.db"))

class TestCreate(TestBase):
    def runTest(self):
        db_file=self.db_file
        sorm=SimpleOrm(db_file=db_file)
        self.assertTrue(os.access(db_file,os.R_OK))

class TestTablename(TestBase):
    def runTest(self):
        sorm=SimpleOrm(db_file=self.db_file)
        self.assertEqual(sorm.tablename(), str(sorm.__class__.__name__))

class TestCreateTable(TestBase):
    def runTest(self):
        sorm=SimpleOrm(db_file=self.db_file)
        sql="DROP TABLE IF EXISTS '%s'" % sorm.tablename()
        sorm.execute(sql)
        sql="CREATE TABLE %s (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR[255], age INTEGER)" % sorm.tablename()
        sorm.execute(sql)

        sorm.execute("pragma %s" % sorm.tablename())

class TestColumnInfo(TestBase):
    def runTest(self):
        sorm=SimpleOrm(db_file=self.db_file)
        info=sorm.column_info()
        self.assertEqual(info['id'],'INTEGER')
        self.assertEqual(info['name'],'VARCHAR[255]')
        self.assertEqual(info['age'],'INTEGER')

if __name__=='__main__':
    unittest.main()

