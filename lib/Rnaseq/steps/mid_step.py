from Rnaseq import *
class mid_step(Step):

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.sh_template='mid_step.tmpl'
        self.usage=''
