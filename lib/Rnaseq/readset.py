#-*-python-*-

import yaml, socket, os
from dict_like import dict_like
from templated import templated

class Readset(dict_like, templated):
    attrs={'name':None,
           'description':None,
           'type':'readset',
           'suffix':'syml',
           }

    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

