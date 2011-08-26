import unittest, os, sys, re

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

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
            inputs=[self.evoque_something(rs, x) for x in step.input_list()]
            target=re.sub('\.\w+$', '.'+rs.format, rs.reads_file)
            self.assertIn(target, inputs)

            outputs=[self.evoque_something(rs, x) for x in step.output_list()]
            o=re.sub('\.\w$', '.'+rs.format, inputs[0])
            self.assertIn(o, outputs)

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

