from Rnaseq import *

class mapsplice2(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='mapsplice2'
        self.sh_template='mapsplice2.tmpl'
