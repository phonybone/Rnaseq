from Rnaseq import *

class extract_significant(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        usage='''
grep 'yes$$' ${inputs[0]} > ${ID}.significant
        '''
        return usage

    def output_list(self):
        return ['${ID}.significant']
    
