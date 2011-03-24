#-*-python-*-

import yaml, socket, os
from dict_like import dict_like
from templated import templated

class Readset(templated, dict_like):
    attrs={'name':None,
           'description':None,
           'type':'readset',
           'suffix':'syml',
           'columns':{'name':'VARCHAR[255]',
                      'description':'TEXT'}
           }

    def __init__(self,**args):
        dict_like.__init__(self,**args)

    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

