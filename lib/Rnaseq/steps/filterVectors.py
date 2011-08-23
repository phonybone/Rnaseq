from Rnaseq import *
from Rnaseq.steps.align_filter import align_filter

class filterVectors(align_filter):
    def __init__(self, **kwargs):
        align_filter.__init__(self,**kwargs)
        self.name='filterVectors'
        self.description='filter vectors'
        self.ewbt='UniVec_Core'
        self.blat_index='solexa_primers.2bit'


    def output_list(self,*args):
        return ['${ID}.vector_BAD.${format}']

    
