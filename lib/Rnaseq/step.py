#-*-python-*-


from dict_like import *
from templated import *

class Step(dict_like, templated):
    attrs={'name':None,
           }

    def load(self):
        templated.load(self)

    def sh_cmd(self):
        pass
    
