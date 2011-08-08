from Rnaseq import *

class sort_by_significance(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        usage='''
sort -k14 -r ${inputs[0]} > ${ID}.sorted.sig
        '''
        return usage

    def output_list(self,*args):
        return ['${ID}.sorted.sig']
    
