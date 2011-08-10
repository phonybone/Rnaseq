import unittest, os, sys



if os.path.dirname(__file__)=='':       # running in local directory
    root_dir=(os.path.normpath(os.getcwd()+'/../..'))
else:
    root_dir=(os.path.normpath(os.path.dirname(__file__)+'/../..'))
print "root_dir is %s" % root_dir
sys.path.append(os.path.join(root_dir, 'lib')
sys.path.append(os.path.join(root_dir, 'ext_libs')

from Rnaseq import *
from RnaseqGlobals import *
from warn import *
from run_pipeline import *

class TestPruneAll(unittest.TestCase):
    readset_file='paired1.syml'
    pipeline_name='touch3'
    
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/%s' % self.readset_file)[0]
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()

        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        for pr in prs:
            session.delete(pr)
        session.commit()
        
    def test_setup(self):
        self.assertEqual(self.pipeline.name, self.pipeline_name)

        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        self.assertEqual(len(prs),0)

    def test_input_conversion(self):
        run_pipeline(self.pipeline)

suite = unittest.TestLoader().loadTestsFromTestCase(TestPruneAll)
unittest.TextTestRunner(verbosity=2).run(suite)


        

