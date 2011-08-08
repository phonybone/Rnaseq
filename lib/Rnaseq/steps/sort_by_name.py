from Rnaseq import *

class sort_by_name(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        usage='''
sort -k3 ${inputs[0]} > ${ID}.sorted.name
        '''
        return usage

    def output_list(self, *args):
        return ['${ID}.sorted.name']
    
