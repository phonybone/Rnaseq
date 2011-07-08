from Rnaseq import *
from Rnaseq.steps.fq_all2std import fq_all2std

class export2fq(fq_all2std):
    export=['format']
    def __init__(self, **kwargs):
        kwargs['cmd']='solexa2fastq'
        kwargs['format']='fq'
        kwargs['description']='convert an Illumina export file to FASTQ format'
        fq_all2std.__init__(self,**kwargs)
        
        
