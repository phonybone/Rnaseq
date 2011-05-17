from Rnaseq import *

class header(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='header'
        self.usage=''
        self.force='True'
        self.skip_success_check='True'
        self.sh_template='header.tmpl'
        
