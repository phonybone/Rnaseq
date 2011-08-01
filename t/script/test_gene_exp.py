import unittest, os, yaml
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestGeneExp(unittest.TestCase):
    readset_file=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+'/../fixtures/readsets/gene_exp.syml')
    pipeline_name='gene_exp'
    
    
    def setUp(self):
        self.argv=RnaseqGlobals.initialize(__file__, testing=True, opt_list=['run', '-v', '-r', self.readset_file, '-p', self.pipeline_name, '-d'])
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir

        # remove files to be created:
        # we just happen to know where the files will be created...
        self.created_files=['gene_exp.diff.1K.significant', 'gene_exp.err', 'gene_exp.out', 'gene_exp.gene_exp.sh']
        for f in self.created_files:
            try: os.remove(os.path.join(RnaseqGlobals.root_dir(),'t','fixtures','data',f))
            except OSError as ioe:
                if re.search('No such file',str(ioe)): pass
                else: raise ioe
        print >> sys.stderr, "output files removed in setup"

        # clear out the database:
        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        for pr in prs:
            session.delete(pr)
        session.commit()

    def o_test_setup(self):
        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        self.assertEqual(len(prs), 0)

        srs=session.query(StepRun).all()
        self.assertEqual(len(srs), 0)

        
    def test_input_conversion(self):
        session=RnaseqGlobals.get_session()

        # create the Command object and run it:
        cf=CmdFactory(program='rnaseq')
        cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
        cmd=cf.new_cmd('run')
        cmd.run(self.argv, config=RnaseqGlobals.config)

        # put in checks to see that the provenance db got updated correctly
        pipeline_run_id=RnaseqGlobals.conf_value('pipeline_run_id')
        self.assertTrue(pipeline_run_id>0)

        # verify that pipeline ran successfully:
        pipeline_run=session.query(PipelineRun).filter_by(id=pipeline_run_id).first()
        self.assertEqual(pipeline_run.__class__.__name__, 'PipelineRun')
        self.assertEqual(pipeline_run.label, 'gene_exp')
        self.assertEqual(pipeline_run.status, 'finished')
        self.assertTrue(pipeline_run.successful)

        # verify check run objects:
        step_runs=session.query(StepRun).filter_by(pipeline_run_id=pipeline_run_id).all()
        self.assertEqual(len(step_runs),5)

        self.assertEqual(step_runs[0].step_name, 'header')
        self.assertEqual(step_runs[0].status, 'finished')
        self.assertTrue(step_runs[0].successful)

        self.assertEqual(step_runs[1].step_name, 'extract_significant')
        self.assertTrue(step_runs[1].successful)
        self.assertEqual(step_runs[1].status, 'finished')

        self.assertEqual(step_runs[2].step_name, 'sort_by_name')
        self.assertTrue(step_runs[2].successful)
        self.assertEqual(step_runs[2].status, 'finished')

        self.assertEqual(step_runs[3].step_name, 'sort_by_sample')
        self.assertTrue(step_runs[3].successful)
        self.assertEqual(step_runs[3].status, 'finished')

        self.assertEqual(step_runs[4].step_name, 'footer')
        self.assertTrue(step_runs[4].successful)
        self.assertEqual(step_runs[4].status, 'finished')
        
        
        # put in checks to see that the correct files got created
        for f in self.created_files:
            self.assertTrue(os.access(os.path.join(RnaseqGlobals.root_dir(),'t','fixtures','data',f), os.R_OK))

            

suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneExp)
unittest.TextTestRunner(verbosity=2).run(suite)


        

