from Rnaseq import *
from Rnaseq.steps.test_step import test_step

class step3(test_step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='step3'

    def output_list(self):
        return ['${ID}.step3a.${format}','${ID}.step3b.${format}']
