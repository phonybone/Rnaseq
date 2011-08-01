from Rnaseq import *

class footer(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='footer'
        self.force=True
        self.skip_success_check=False

    def usage(self, context):
        return "echo %s done" % self.pipeline.name

    def output_list(self):
        return []
    
