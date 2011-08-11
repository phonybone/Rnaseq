import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

# sqlalchemy-related test that verifies pipeline object gets inserted into db,
# and pipeline.id is set.
# fixme:
# add use_existing to call to table.create (or something)
# get rid of __file__ refs, replace with 

class TestCreate(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        templated.template_dir=RnaseqGlobals.root_dir()+"/t/fixtures/templates"

        readset_file=RnaseqGlobals.root_dir()+"/t/fixtures/readsets/readset1.syml"
        self.readset=Readset.load(readset_file)[0]
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()
        session=RnaseqGlobals.get_session()

        # delete all pre-existing pipeline objects from the db:
        plist=session.query(Pipeline)
        for p in plist:
            session.delete(p)
        session.commit()

    def test_pipeline_id(self):
        pipeline=self.pipeline
        try: id=pipeline.id 
        except AttributeError: self.assertTrue(True)
            
        session=RnaseqGlobals.get_session()
        

        session.add(pipeline)
        session.commit()
        session.flush()

        self.assertEqual(pipeline.id, 1)

        mpipeline=session.merge(pipeline)
        self.assertEqual(mpipeline.id, 1)

        

suite = unittest.TestLoader().loadTestsFromTestCase(TestCreate)
unittest.TextTestRunner(verbosity=2).run(suite)
