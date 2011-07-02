import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

class TestAlchemy(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        templated.template_dir=RnaseqGlobals.root_dir()+'/t/fixtures/templates'

        os.chdir(RnaseqGlobals.root_dir()+'/t/fixtures/readsets')

        filename=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset_rel_glob.syml'
        rlist=Readset.load(filename)
        readset=rlist[0]
        self.readset=readset
        
        self.session=RnaseqGlobals.get_session()
        rlist=self.session.query(Readset)
        for rs in rlist:
            self.session.delete(rs)
        self.session.commit()

    def dont_test_insert(self):
        self.session.add(self.readset)
        self.session.commit()

    def dont_test_query(self):
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
        


suite = unittest.TestLoader().loadTestsFromTestCase(TestAlchemy)
unittest.TextTestRunner(verbosity=2).run(suite)

