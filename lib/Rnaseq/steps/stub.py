from Rnaseq import *

class stub(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        usage='''
        '''
        return usage

    def output_list(self,*args):
        return ['']
    
