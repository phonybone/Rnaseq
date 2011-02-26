import os, yaml, unittest
from superyaml import *
from warn import *
from helpers import hashslice

class TestSuperyaml(unittest.TestCase):
    def setUp(self):
        pass

    def test_composite(self):
        sy=superyaml(domain='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates')
        readset=sy.load('readset.syml',{})

        bowtie=sy.load('bowtie.syml',readset)
        warn("bowtie 1",yaml.dump(bowtie))
        self.assertEquals(bowtie['exe'],'bowtie','got d[exe]=%s, expected "bowtie"' % bowtie['exe'])

        bowtie.update(readset)
        bowtie=sy.load('bowtie.syml',bowtie)
        warn("bowtie 2",yaml.dump(bowtie))

        expected=("%(exe)s %(ewbt)s %(args)s" % hashslice(bowtie,'exe','ewbt','args')) + " ${input} ${output}"
        warn("expected is %s" % expected)
        self.assertEquals(bowtie['usage'], expected,
                          'got bowtie[usage]=%s, expected %s' % (bowtie['usage'], expected))


if __name__=='__main__':
    unittest.main()                              # unittest.main(), actually
