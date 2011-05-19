from Rnaseq import *
from Rnaseq.steps.align_filter import align_filter

class ribosomal_mit(align_filter):
    def __init__(self,**kwargs):
        align_filter.__init__(self,**kwargs)
        self.name='ribosomal_mit'
        self.description='remove rRNA/MT matches'
        self.ewbt='human.GRCh37.61.rRNA-MT'
        self.blat_index='human.GRCh37.61.rRNA-MT.2bit'
