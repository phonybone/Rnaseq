import unittest, os, sys
dir=os.path.normpath(os.path.dirname(os.path.abspath(__file__))+"/../..")
sys.path.append(os.path.join(dir+'/lib'))
sys.path.append(os.path.join(dir+'/ext_libs'))

from Rnaseq import *
from RnaseqGlobals import *
from warn import *
from evoque_helpers import evoque_template

class NullDevice():
    def write(self, s):
        pass

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

    def test_missing_value(self):
        template="This has a ${missing} value"
        vars={'not_missing':1}
        try:
            string=evoque_template(template, vars)
            self.fail()
        except exceptions.NameError as e:
#            warn("caught %s (%s)" % (e, type(e)))
            self.assertRegexpMatches(str(e), "name 'missing' is not defined")



suite = unittest.TestLoader().loadTestsFromTestCase(TestEvoqueHelpers)
unittest.TextTestRunner(verbosity=2).run(suite)


        

