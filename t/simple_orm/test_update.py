import unittest, os
from Rnaseq import *
from warn import *
from RnaseqGlobals import RnaseqGlobals

class TestBase(unittest.TestCase):
    def setUp(self):
        usage="testing: "+__file__
        RnaseqGlobals.initialize(usage)

        self.db_file=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),RnaseqGlobals.conf_value('testing','test_db'))
        readset=Readset(name='readset', db_file=self.db_file).load()
        self.readset=readset
        #print "readset is %s" % readset
        

        readset.execute(sql)
        print "table %s created" % readset.tablename()


class TestInsert(TestBase):
    def runTest(self):
        readset=self.readset
        self.assertIs(readset.__class__,Readset)
        readset.insert()

        sql="SELECT * FROM %s" % readset.tablename()
        readset.execute(sql)

        for row in readset.cursor.fetchall():
            print "row: ",row
            self.assertEqual(row[1],readset.name)
            self.assertEqual(row[2],readset.description)


class TestInsert2(TestBase):
    def runTest(self):
        readset=self.readset
        print "poof"


if __name__=='__main__':
    unittest.main()
        


