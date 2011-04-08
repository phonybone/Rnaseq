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
        self.pipeline=Pipeline(name='juan', readset=readset).load()
        
        self.session=RnaseqGlobals.get_session()
        RnaseqGlobals.engine.execute("DROP TABLE IF EXISTS %s" % Pipeline.__tablename__)
        
        Pipeline.create_table(RnaseqGlobals.metadata, RnaseqGlobals.engine)
        print "Pipeline table created"
        

class TestInsert(TestCreate):
    def runTest(self):
        self.session.add(self.pipeline)
        self.session.commit()

class TestQuery(TestCreate):
    def runTest(self):
        session=self.session
        readset=self.readset
        session.add(self.pipeline)
        session.commit()

        l=session.query(Pipeline).filter_by(name=pipeline.name).all()
        self.assertEqual(len(l), 1)

        pl=l[0]
        for a in ['name', 'description']:
            self.assertEqual(getattr(pl,a), getattr(pipeline,a))
        self.assertEqual(pl.id,1)
        


if __name__=='__main__':
    unittest.main()

