#-*-python-*-

from dict_like import *
from templated import *
from warn import *
import yaml

class Step(dict_like, templated):
    attrs={'name':None,
           'type':'step',
           'pipeline':None,
           }

    def sh_script(self):    
        if 'sh_template' in self.attrs_dict():       # fixme: will this barf if sh_template not defined?
            template_dir='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates/sh_template' # fixme; get value from a config file
            domain=Domain(template_dir)
            template=domain.get_template(self['sh_template'])

            vars=self.attrs_dict()
            vars.update(self.pipeline['rnaseq'])
            vars['sh_cmd']=self.sh_cmdline()
            
            return template.evoque(vars)
        else:
            return None

    def sh_cmdline(self):
        try: 
            sh_cmd=self.usage % self
            self['sh_cmd']=sh_cmd
            return sh_cmd

        except KeyError as e:
            die("Missing value %s in\n%s" % (e.args, yaml.dump(self)))
        except AttributeError as e:
            die("Missing value %s in\n%s" % (e.args, yaml.dump(self)))
        except ValueError as e:
            warn(e)
            warn("%s.usage: %s" % (self.name,self.usage))
            die("%s.keys(): %s" % (self.name, ", ".join(self.__dict__.keys())))

    def sh_cmd(self):
        script=self.sh_script()
        if script!=None: return script
        else: return self.sh_cmdline()
