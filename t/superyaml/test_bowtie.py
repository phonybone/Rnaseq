import os, yaml, unittest
from superyaml import *
from warn import *

class TestSuperyaml(unittest.TestCase):
    def setUp(self):
        pass

    def test_bowtie(self):
        sy=superyaml(domain='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates')
        d_sy=sy.load('bowtie.syml',{})
        warn(yaml.dump(d_sy))

        d_sy=sy.load('bowtie.syml',d_sy)
        warn(yaml.dump(d_sy))
        self.assertEquals(d_sy['exe'],'bowtie','got d[exe]=%s, expected "bowtie"' % d_sy['exe'])

if __name__=='__main__':
    unittest.main()                              # unittest.main(), actually
