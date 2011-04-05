#-*-python-*-

import yaml, socket, os
from dict_like import dict_like
from templated import templated

class Readset(templated):
    def __init__(self,**args):
        templated.__init__(self,**args)
        self.suffix='syml'
        self.type='readset'
    
    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

