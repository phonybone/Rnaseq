import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)

        self.readset=Readset(reads_file=os.path.abspath(__file__+'/../../readset/s_1_export.txt'),
                             readlen=75,
                             working_dir='rnaseq_wf')
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()
        
        self.session=RnaseqGlobals.get_session()

        
        Pipeline.create_table(RnaseqGlobals.metadata, RnaseqGlobals.engine)
        print "Pipeline table created"
        

class TestId(TestCreate):
    def runTest(self):
        pipeline=self.pipeline
        try: id=pipeline.id 
        except AttributeError: self.assertTrue(True)
            
        session=self.session
        session.add(pipeline)
        session.commit()
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

