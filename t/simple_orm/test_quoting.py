import unittest, os, re
from Rnaseq import *
from warn import *

class TestBase(unittest.TestCase):
    def setUp(self):
        self.db_file=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../fixtures/dbs/simple_orm.db"))
        self.sorm=SimpleOrm(db_file=self.db_file)


class TestFields(TestBase):
    def runTest(self):
        readset=Readset(name='readset')
        self.assertIs(readset.__class__,Readset)
        fields1=sorted(re.split(", ",readset.fields_str()))
        fields2=sorted(readset.attributes().keys())
        self.assertEqual(fields1, fields2)

class TestValues(TestBase):
    def runTest(self):
        readset=Readset(name='readset')
        self.assertIs(readset.__class__,Readset)
        values1=sorted(re.split(", ",readset.values_str()))
        values2=sorted("'%s'" % x for x in sorted(readset.attributes().values()))
        self.assertEqual(values1, values2)

        

if __name__=='__main__':
    unittest.main()
        


