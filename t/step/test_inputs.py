import unittest, os, sys, yaml

sys.path.append(os.path.normpath(os.path.abspath(__file__)+"/../../../lib"))
from Rnaseq import *
from RnaseqGlobals import *
from warn import *

class TestInputs(unittest.TestCase):
    def setUp(self):
        argv=RnaseqGlobals.initialize(__file__, testing=True)       # not to be confused with sys.argv
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir

        readset_file=RnaseqGlobals.root_dir()+"/t/fixtures/readsets/readset12_nwd.syml"
        self.rlist=Readset.load(readset_file)


    def test_list_expansion(self):
        for rs in self.rlist:

            pipeline=Pipeline(name='filter', readset=rs).load_steps()
            step=pipeline.step_with_name('export2fq')

            self.assertTrue(isinstance(step, Step))
            inputs=[self.evoque_something(rs, x) for x in step.inputs()]
            self.assertIn(rs.reads_file,inputs)

            outputs=[self.evoque_something(rs, x) for x in step.outputs()]
            self.assertIn("%s.fq" % rs.reads_file, outputs)

    def evoque_something(self, readset, template):
        domain=Domain(os.getcwd(), errors=4) # we actually don't care about the first arg
        domain.set_template('name', src=template)
        tmp=domain.get_template('name')

        vars={}
        vars.update(self.__dict__)
        vars.update(readset.__dict__)
        output=tmp.evoque(vars)
        return output
        


suite = unittest.TestLoader().loadTestsFromTestCase(TestInputs)
unittest.TextTestRunner(verbosity=2).run(suite)

