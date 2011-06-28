from Rnaseq import *
from Rnaseq.steps.fq_all2std import fq_all2std

class export2fq(fq_all2std):
    export=['format']
    def __init__(self, **kwargs):
        fq_all2std.__init__(self,**kwargs)
        self.description='convert an Illumina export file to FASTQ format'
        self.cmd='solexa2fastq'
        self.format='fq'
        
        
