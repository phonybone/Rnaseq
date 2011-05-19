from Rnaseq import *
class pipeline_start(Step):

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.sh_template='pipeline_start.tmpl'
        self.usage=''
