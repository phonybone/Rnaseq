#-*-python-*-

import yaml, time, re
import Rnaseq
from RnaseqGlobals import RnaseqGlobals
from dict_like import *
from templated import *
from warn import *

class Step(dict_like, templated):
    attrs={'name':None,
           'description':None,
           'type':'step',
           'suffix':'syml',
           'pipeline':None,
           'force': False,
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
            if os.path.abspath(self.exe)!=self.exe:
                self.exe=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'bin', self.exe)
        except AttributeError as ae:
            pass

        try:
            return self.usage % self   

        # fixme: you don't really know what you're doing in these except blocks...
        except KeyError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, self.name))
        except AttributeError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, self.name))
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
        if 'input' not in self.attributes(): return []
        return re.split("[,\s]+",self.input)

    def outputs(self):
        if 'output' not in self.attributes(): return []
        return re.split("[,\s]+",self.output)
    
    def creates(self):
        if 'create' not in self.attributes(): return []
        return re.split("[,\s]+",self.create)
    
    # current: return true if all of the step's outputs are older than all
    # of the steps inputs AND the step's exe:
    def is_current(self):
        if self.force: return False
        latest_input=0
        earliest_output=time.time()

        for input in self.inputs():
            try:
                mtime=os.stat(input).st_mtime
            except OSError as ose:
                return False            # missing/unaccessible inputs constitute not being current
            
            if mtime > latest_input:
                latest_input=mtime

            exe_file=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'bin', self.exe)
            exe_mtime=os.stat(exe_file).st_mtime
            if exe_mtime > latest_input:
                latest_input=exe_mtime

        for output in self.outputs():
            try:
                stat_info=os.stat(output)
                if (stat_info.st_mtime < earliest_output):
                    earliest_output=stat_info.st_mtime
            except OSError as ose:
                return False            # missing/unaccessible outputs definitely constitute not being current

        #print "final: latest_input is %s, earliest_output is %s" % (latest_input, earliest_output)
        return latest_input<earliest_output
