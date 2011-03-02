#-*-python-*-

from dict_like import *
from templated import *
from warn import *
import yaml

class Step(dict_like, templated):
    attrs={'name':None,
           'type':'step'
           }

    def sh_cmd(self):
        try: 
            sh_cmd=self.usage % self
            self['sh_cmd']=sh_cmd
            return sh_cmd

        except KeyError as e:
            die("Missing value %s in\n%s" % (e.args, yaml.dump(self)))
        except ValueError as e:
            warn(e)
            warn("%s.usage: %s" % (self.name,self.usage))
            die("%s.keys(): %s" % (self.name, ", ".join(self.__dict__.keys())))
