import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        readset=Readset(name='readset').load(vars=RnaseqGlobals.config)
        self.readset=readset
        
        self.session=RnaseqGlobals.get_session()
        RnaseqGlobals.engine.execute("DROP TABLE IF EXISTS %s" % Readset.__tablename__)
        
        readset.create_table(RnaseqGlobals.metadata, RnaseqGlobals.engine)
        print "Readset table created"
        

class TestInsert(TestCreate):
    def runTest(self):
        self.session.add(self.readset)
        self.session.commit()

class TestQuery(TestCreate):
    def runTest(self):
        session=self.session
        readset=self.readset
        session.add(self.readset)
        session.commit()

        l=session.query(Readset).filter_by(name=readset.name).all()
        self.assertEqual(len(l), 1)

        r=l[0]
        for a in ['name', 'org', 'readlen', 'reads_file', 'working_dir']:
            self.assertEqual(getattr(r,a), getattr(readset,a))
        self.assertEqual(r.id,1)
        


if __name__=='__main__':
    unittest.main()

