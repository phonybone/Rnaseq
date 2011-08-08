from Rnaseq import *
from Rnaseq.steps.align_filter import align_filter

class repeats_consensus(align_filter):
    def __init__(self,**kwargs):
        align_filter.__init__(self,**kwargs)
        self.name='repeats_consensus'
        self.description='remove repeats'
        self.ewbt='human_RepBase15.10'
        self.blat_index='human_RepBase15.10.2bit'

    def output_list(self,*args):
        return ['${ID}.repeats_BAD.${format}']

    
