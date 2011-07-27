import unittest, os
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
        
    def test_input_conversion(self):
        # create the Command object and run it:
        cf=CmdFactory(program='rnaseq')
        cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
        cmd=cf.new_cmd('run')
        cmd.run(self.argv, config=RnaseqGlobals.config)
        print "yay"

        # put in checks to see that the provenance db got updated correctly
        session=RnaseqGlobals.get_session()
        for pr in session.query(PipelineRun).all():
            pass
        
        # put in checks to see that the correct files got created
        for f in self.created_files:
            self.assertTrue(os.access(os.path.join(RnaseqGlobals.root_dir(),'t','fixtures','data',f), os.R_OK))

            

suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneExp)
unittest.TextTestRunner(verbosity=2).run(suite)


        

