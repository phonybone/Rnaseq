import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestCreate(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)

        readset_file=os.path.join(RnaseqGlobals.root_dir(),'t','fixtures','readsets','readset1.syml')
        self.readset=Readset.load(readset_file)[0]
        self.pipeline=Pipeline(name='juan', readset=self.readset).load_steps()

        session=RnaseqGlobals.get_session()
        ps=session.query(Pipeline).all()
        for p in ps:
            session.delete(p)
        session.commit()

    def test_insert(self):
        session=RnaseqGlobals.get_session()
        session.add(self.pipeline)
        session.commit()

    def test_query(self):
        session=RnaseqGlobals.get_session()
        readset=self.readset
        session.add(self.pipeline)
        session.commit()

        pipeline=self.pipeline
        l=session.query(Pipeline).filter_by(name=pipeline.name).all()
        self.assertEqual(len(l), 1)

        pl=l[0]
        for a in ['name', 'description']:
            self.assertEqual(getattr(pl,a), getattr(pipeline,a))
        self.assertEqual(pl.id,1)
        


suite = unittest.TestLoader().loadTestsFromTestCase(TestCreate)
unittest.TextTestRunner(verbosity=2).run(suite)
