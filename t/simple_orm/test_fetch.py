import unittest, os
from Rnaseq import *
from warn import *
from RnaseqGlobals import RnaseqGlobals

class TestBase(unittest.TestCase):
    def setUp(self):
        usage=""
        RnaseqGlobals.initialize(usage)

        self.db_file=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),RnaseqGlobals.conf_value('testing','test_db'))
        readset=Readset(name='readset', db_file=self.db_file).load()

        self.readset=readset
        if not readset.table_exists():
            raise ProgrammerGoof("table %s doesn't exist" % readset.tablename())

class TestFetch(TestBase):
    def runTest(self):
        readset=self.readset
        self.assertIs(readset.__class__,Readset)

        



if __name__=='__main__':
    unittest.main()
        


