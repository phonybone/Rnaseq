import sys, unittest, os

dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *
import yaml

class TestBase(unittest.TestCase):
    readset_name='readset1.syml'
    pipeline_name='test_convert_inputs'
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        
        self.readset=Readset.load(RnaseqGlobals.root_dir()+'/t/fixtures/readsets/'+self.readset_name)[0]
#        os.environ['DEBUG']='True'
        self.pipeline=Pipeline(name=self.pipeline_name, readset=self.readset).load_steps()
        # errors=self.pipeline.convert_io()
#        del os.environ['DEBUG']

#         if len(errors)>0:
#             print "errors in setup:"
#             print "\n  ".join(errors)
#             self.fail()


    def test_setup(self):
        self.assertEqual(self.readset.name, self.readset_name)
        self.assertEqual(self.pipeline.name, self.pipeline_name)

    def test_input_conversion(self):
        c=self.pipeline.context
        readset=self.pipeline.readset
        # print "test_convert_inputs: context:\n%s" % yaml.dump(c)

        self.assertEqual(c.inputs['header'],[])
        target=os.path.join(readset.working_dir, os.path.basename(readset.reads_files[0]))
        self.assertEqual(c.outputs['header'], [target])

        self.assertEqual(c.inputs['step1'],c.outputs['header'])
        self.assertEqual(c.outputs['step1'],['${ID}.step1.${format}'])
    
        self.assertEqual(c.inputs['step2'],c.outputs['step1'])
        self.assertEqual(c.outputs['step2'],['${ID}.step2a.${format}','${ID}.step2b.${format}'])

        self.assertEqual(c.inputs['step3'],[c.outputs['step2'][0]])
        self.assertEqual(c.outputs['step3'],['${ID}.step3a.${format}','${ID}.step3b.${format}'])

        self.assertEqual(c.inputs['step4'][0],c.outputs['step2'][1])
        self.assertEqual(c.inputs['step4'][1],c.outputs['step3'][0])
        self.assertEqual(c.inputs['step4'][2],c.outputs['step3'][1])
        self.assertEqual(c.outputs['step4'],['${ID}.step4.${format}'])

        self.assertEqual(c.inputs['step5'][0],c.outputs['step1'][0])
        self.assertEqual(c.inputs['step5'][1],c.outputs['step2'][0])
        self.assertEqual(c.outputs['step5'],['${ID}.step5.${format}'])

        self.assertEqual(c.inputs['footer'],[])
        self.assertEqual(c.outputs['footer'],[])

    def test_input_out_of_range(self):
        try:
            self.pipeline=Pipeline(name='input_index_out_of_range', readset=self.readset).load_steps()
            self.fail()
        except ConfigError as ce:
            self.assertRegexpMatches(str(ce), 'step step3: outputs .* out of range')

suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
unittest.TextTestRunner(verbosity=2).run(suite)


        

