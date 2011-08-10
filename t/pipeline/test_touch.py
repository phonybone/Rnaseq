import unittest, os, time, sys

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TouchStep(unittest.TestCase):
    print "os.path.dirname(__file__) is %s" % os.path.dirname(__file__)
    if os.path.dirname(__file__)=='': 
        readset_file=os.path.abspath(os.path.dirname(__file__)+'../fixtures/readsets/readset_rel_glob.syml')
    else:
        readset_file=os.path.abspath(os.path.dirname(__file__)+'/../fixtures/readsets/readset_rel_glob.syml')
        
    pipeline_name='touch3'
    
    
    def setUp(self):
        self.argv=RnaseqGlobals.initialize(__file__, testing=True, opt_list=['run', '-f', '-r', self.readset_file, '-p', self.pipeline_name, '-q', '-d'])
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        #print "test_touch: readset_file is %s" % self.readset_file
        self.readset_list=Readset.load(self.readset_file)



    def test_setup(self):
        self.assertEqual(len(self.readset_list),1)

    def test_input_conversion(self):
        before_run=time.time()

        # create the Command object and run it:
        cf=CmdFactory(program='rnaseq')
        cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
        cmd=cf.new_cmd('run')
        cmd.run(self.argv, config=RnaseqGlobals.config)


        rs=self.readset_list[0]
        for f in rs.reads_files:
            mod_time=os.stat(f).st_mtime
            self.assertGreaterEqual(mod_time, before_run)
            print "checked %s" % f

    dead_code='''
    def tearDown(self):
        session=RnaseqGlobals.get_session()
        plist=session.query(PipelineRun)
        for p in plist:
            session.delete(p)
        session.commit()
'''

suite = unittest.TestLoader().loadTestsFromTestCase(TouchStep)
unittest.TextTestRunner(verbosity=2).run(suite)


        

