import unittest, os, yaml
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestGeneExp(unittest.TestCase):
    readset_file=os.path.abspath(os.path.dirname(__file__)+'../fixtures/readsets/gene_exp.syml')
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
        print >> sys.stderr, "db cleared"

    def o_test_setup(self):
        session=RnaseqGlobals.get_session()
        prs=session.query(PipelineRun).all()
        self.assertEqual(len(prs), 0)

        srs=session.query(StepRun).all()
        self.assertEqual(len(srs), 0)

    def test_mid_step(self):
        session=RnaseqGlobals.get_session()

        # create the Command object and run it:
        cf=CmdFactory(program='rnaseq')
        cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
        cmd=cf.new_cmd('run')
        cmd.run(self.argv, config=RnaseqGlobals.config)

        # get output file:
        output_file=os.path.join(RnaseqGlobals.root_dir(), 't', 'fixtures', 'data', 'gene_exp.out')
        self.assertTrue(os.access(output_file, os.R_OK))
        f=open(output_file)
        output=f.read()
        f.close()
#         print '**********************************'
#         print output
#         print '**********************************'

        # get the pipeline_run object:
        pipeline_run=session.query(PipelineRun).get(RnaseqGlobals.conf_value('pipeline_run_id'))
        self.assertIsInstance(pipeline_run, PipelineRun)

        # check for notice of every created output file:
        for sr in pipeline_run.step_runs:
            for o in sr.file_outputs:
                self.assertRegexpMatches(output, '%s created' % o.path)

suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneExp)
unittest.TextTestRunner(verbosity=2).run(suite)


        

