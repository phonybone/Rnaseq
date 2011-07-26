import unittest, os
from Rnaseq import *
from RnaseqGlobals import *
from warn import *
from evoque_helpers import evoque_template

class TestEvoqueHelpers(unittest.TestCase):
    
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        template_dir=RnaseqGlobals.abs_dir('testing', 'template_dir')
        templated.template_dir=template_dir
        

    def test_basic(self):
        template="This is a ${adjective} template"
        vars={'adjective': 'simple'}
        string=evoque_template(template, vars)
        self.assertEqual(string, 'This is a simple template')

suite = unittest.TestLoader().loadTestsFromTestCase(TestEvoqueHelpers)
unittest.TextTestRunner(verbosity=2).run(suite)


        

