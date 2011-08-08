from Rnaseq import *

class touch(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        self.filelist=' '.join(context.inputs)
        usage='''
touch %(filelist)s
''' % { 'filelist': self.filelist}
        return usage

    def output_list(self, *args):
        return self.input_list()
    
