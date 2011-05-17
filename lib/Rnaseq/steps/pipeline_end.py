from Rnaseq import *
class pipeline_end(Step):

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.sh_template='pipeline_end.tmpl'
        self.usage=''
