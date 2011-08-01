from Rnaseq import *
from Rnaseq.steps.test_step import test_step

class step4(test_step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='step4'
        
