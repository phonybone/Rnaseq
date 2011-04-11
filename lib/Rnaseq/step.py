#-*-python-*-

import yaml, time, re
from RnaseqGlobals import RnaseqGlobals
from dict_like import *
from templated import *
from warn import *
from sqlalchemy import *
from table_base import TableBase

class Step(templated, TableBase):
    def __init__(self,*args,**kwargs):
        templated.__init__(self,*args,**kwargs)
        self.type='step'
        self.suffix='syml'
        if not hasattr(self,'force'): self.force=False


    ########################################################################
    __tablename__='step'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    description=Column(String)
    
    @classmethod
    def create_table(self, metadata, engine):
        step_table=Table(self.__tablename__, metadata,
                         Column('id',Integer, primary_key=True),
                         Column('name',String,nullable=False),
                         Column('description', String),
                         )
        metadata.create_all(engine)
        return step_table
    

    

    ########################################################################

    def load(self, **args):
        try: vars=args['vars']
        except KeyError: vars={}
        vars['pipeline']=self.pipeline
        vars['readset']=self.pipeline.readset
        templated.load(self, vars=vars, final=True)

        try:
            ptype=Step(name=self['prototype'], pipeline=self.pipeline)
            ptype.load(vars=vars)
            self.merge(ptype)
        except KeyError:
            pass

        # only things that are defined in step.syml or step.prototype.syml, NOT pipeline.syml
        for a in ['name', 'description', 'interpreter', 'exe', 'usage', 'force', 'sh_template']:
            try:
                setattr(self,a,self[a])
            except:
                pass

        return self

    # If a step needs more than one line to invoke (eg bowtie: needs to set an environment variable),
    # define the set of commands in a template and set the 'sh_template' attribute to point to the template
    # within the templates/sh_templates subdir).  This routine fetches the template and calls evoque on it, and
    # returns the resulting string.
    # If no sh_template is required, return None.
    def sh_script(self, **kwargs):
        if 'sh_template' in self.dict:
            template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),"templates","sh_template")

            domain=Domain(template_dir, errors=4)
            sh_template=self['sh_template']
            template=domain.get_template(sh_template)

            vars={}
            vars.update(self)
            vars.update(self.dict)
            vars['readset']=self.pipeline.readset # fixme: really?
            vars['sh_cmd']=self.sh_cmdline() 
            vars['config']=RnaseqGlobals.config
            vars['pipeline']=self.pipeline
            vars.update(kwargs)
            #print vars

            try:
                script=template.evoque(vars)
                return script
            except NameError as ne:
                raise ConfigError("%s while processing step '%s'" %(ne,self.name))
        else:
            return None

    # use the self.usage formatting string to create the command line that executes the script/program for
    # this step.  Return as a string.  Throws exceptions as die()'s.
    def sh_cmdline(self):
        try:
            usage=self['usage']
            if usage==None:
                usage=''
        except KeyError:
            usage=''

        # look for exe in path, unless exe is an absolute path
        try:
            if os.path.abspath(self.exe)!=self.exe:
                self.exe=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'bin', self.exe)
        except AttributeError as ae:
            pass


        try:
            return usage % self   

        # fixme: you don't really know what you're doing in these except blocks...
        except KeyError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, self.name))
        except AttributeError as e:
            raise ConfigError("Missing value %s in\n%s" % (e.args, self.name))
        except ValueError as e:
            warn(e)
            warn("%s.usage: %s" % (self.name,usage))
            raise "%s.keys(): %s" % (self.name, ", ".join(self.__dict__.keys()))
        except TypeError as te:
            raise ConfigError("step %s: usage='%s': %s" % (self.name, usage, te))


    # entry point to step's sh "presence"; calls appropriate functions, as above.
    def sh_cmd(self, **args):
        echo_part=''
        if 'echo_name' in args and args['echo_name']:
            echo_part="echo step %s 1>&2" % self.name
            
        sh_script=self.sh_script()
        if sh_script==None:
            sh_script=self.sh_cmdline()+"\n"

        script="\n".join([echo_part,sh_script]) # tried using echo_part+sh_script, got weird '>' -> '&gt;' substitutions
        return script

########################################################################

    def inputs(self):
        try: return re.split("[,\s]+",self['input'])
        except: return []

    def outputs(self):
        try: return re.split("[,\s]+",self['output'])
        except: return []
    
    def creates(self):
        try: return re.split("[,\s]+",self['create'])
        except: return []
    
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
