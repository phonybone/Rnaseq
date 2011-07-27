from Rnaseq import *

class sort_by_sample(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        usage='''
sort -k5,6 ${inputs[0]} > ${ID}.sorted.sample
        '''
        return usage

    def output_list(self):
        return ['${ID}.sorted.sample']
    
