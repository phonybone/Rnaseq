import os, yaml, unittest


from templated import *
from warn import *
from Rnaseq import *

class TestTemplated(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_load(self):
        readset=Readset(name='readset',type='readset').load()
        pipeline=Pipeline(name='erange').load(readset)
        bowtie=pipeline.stepByName('bowtie')

        # print "test_all: bowtie is %s" % yaml.dump(bowtie)
        # print "test_all: bowtie sh_cmd is %s" % bowtie.sh_cmd()


    # normally, templated is a mixin class.  But it should be possible to
    # instanciate it independently
    def test_instance(self):
        t=templated(name='bowtie', type='sh_template')
        output=t.eval_tmpl(vars=t)
        # print "t is %s" % t
        # print "output is %s" % output

        readset=Readset(name='readset',type='readset').load()
        pipeline=Pipeline(name='erange').load(readset)
        # print "test_all: pipeline is %s" % yaml.dump(pipeline)
        bowtie=pipeline.stepByName('bowtie')
        output=t.eval_tmpl(vars=pipeline)
        print "output is %s" % output

if __name__=='__main__':
    unittest.main()                              # unittest.main(), actually
        
        
