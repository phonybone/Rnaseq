#-*-python-*-

from dict_like import *
from templated import *
from warn import *
import yaml, time, re

class Step(dict_like, templated):
    attrs={'name':None,
           'description':None,
           'type':'step',
           'pipeline':None,
           }


    def load(self):
        templated.load(self)
        if self.has_attr('prototype'):
            ptype=Step(name=self.prototype)
            ptype.load()
            self.merge(ptype)
        return self

    # If a step needs more than one line to invoke (eg bowtie: needs to set an environment variable),
    # define the set of commands in a template and set the 'sh_template' attribute to point to the template
    # within the templates/sh_templates subdir).  This routine fetches the template and calls evoque on it, and
    # returns the resulting string.
    # If no sh_template is required, return None.
    def sh_script(self):    
        if 'sh_template' in self.attributes():       # fixme: will this barf if sh_template not defined?
            template_dir='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates/sh_template' # fixme; get value from a config file
            domain=Domain(template_dir)
            template=domain.get_template(self['sh_template'])

            vars=self.attributes().copy()
            vars.update(self.pipeline['rnaseq'])
            vars['readset']=self.pipeline.readset
            vars['sh_cmd']=self.sh_cmdline() 
            
            return template.evoque(vars)
        else:
            return None

    # use the self.usage formatting string to create the command line that executes the script/program for
    # this step.  Return as a string.  Throws exceptions as die()'s.
    def sh_cmdline(self):
        if self.usage==None:
            self.usage=''
        try: 
            return self.usage % self   

        except KeyError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, yaml.dump(self)))
        except AttributeError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, yaml.dump(self)))
        except ValueError as e:
            warn(e)
            warn("%s.usage: %s" % (self.name,self.usage))
            raise "%s.keys(): %s" % (self.name, ", ".join(self.__dict__.keys()))


    # entry point to step's sh "presence"; calls appropriate functions, as above.
    def sh_cmd(self, **args):
        script=''
        if 'echo_name' in args and args['echo_name']:
            script+="echo %s step\n" % self.name
        sh_script=self.sh_script()
        if sh_script!=None:  script+=sh_script
        else: script+=self.sh_cmdline()+"\n"
        return script

########################################################################

    def inputs(self):
        return re.split("[,\s]+",self.input)

    def outputs(self):
        return re.split("[,\s]+",self.output)
    
    # current: return true if all of the step's outputs are older than all
    # of the steps inputs AND the step's exe:
    def is_current(self):
        latest_input=0
        earliest_output=time.time()

        for input in self.inputs():
            try:
                stat_info=os.stat(input)
                if stat_info.st_mtime > latest_input:
                    latest_input=stat_info.st_mtime

                stat_info=os.stat(self.exe)
                if stat_info.st_mtime > latest_input:
                    latest_input=stat_info.st_mtime
            except OSError as ose:
                return False            # missing/unaccessible inputs constitute not being current

        for output in self.outputs:
            try:
                stat_info=os.stat(output)
                if (stat_info.st_mtime < earlist_output):
                    earliest_output=stat_info.st_mtime
            except OSError as ose:
                return False            # missing/unaccessible outputs definitely constitute not being current
            
        return latest_input<earliest_output
