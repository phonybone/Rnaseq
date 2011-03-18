#-*-python-*-

import yaml
from dict_like import dict_like
from templated import templated

class Readset(dict_like, templated):
    attrs={'name':None,
           'description':None,
           'type':'readset',
           }
    
