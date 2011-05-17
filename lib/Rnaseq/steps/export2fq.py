from Rnaseq import *
from Rnaseq.steps.fq_all2std import fq_all2std

class export2fq(fq_all2std):
    def __init__(self, **kwargs):
        fq_all2std.__init__(self,**kwargs)
        self.args='solexa2fastq'
