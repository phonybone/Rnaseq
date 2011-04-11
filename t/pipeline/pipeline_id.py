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
        

class TestId(TestCreate):
    def runTest(self):
        pipeline=self.pipeline
        try: id=pipeline.id 
        except AttributeError: self.assertTrue(True)
            
        session=self.session
        session.add(pipeline)
        session.flush()

        try:
            print "pipeline.id is %s" % pipeline.id
        except AttributeError:
            print "pipeline has no id attr"

        mpipeline=session.merge(pipeline)
        try:
            print "mpipeline.id is %s" % mpipeline.id
        except AttributeError:
            print "mpipeline has no id attr"
        

        

if __name__=='__main__':
    unittest.main()

