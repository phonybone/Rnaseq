from Rnaseq import *
from Rnaseq.steps.align_filter import align_filter

class remove_erccs(align_filter):
    def __init__(self,**kwargs):
        align_filter.__init__(self,**kwargs)
        self.name='remove_erccs'
        self.description='remove ercc reads'
        self.ewbt='ERCC_reference_081215'
        self.blat_index='ERCC_reference_081215.2bit'


