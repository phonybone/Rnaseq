from Rnaseq import *

class footer(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='footer'
        self.usage=''
        self.force='True'
        self.skip_success_check='True'
        self.sh_template='footer.tmpl'
