#-*-python-*-

import yaml, time, re
from RnaseqGlobals import RnaseqGlobals
#from templated import *
from warn import *
from Rnaseq import *
from step_run import *

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from hash_helpers import obj2dict

class Step(dict):                     # was Step(templated)
    def __init__(self,*args,**kwargs):
        for k,v in kwargs.items():
            try: setattr(self,k,v)      # something in alchemy can eff this up
            except Exception as e: print "templated.__init__: caught %s" % e
        try:                    # something in alchemy can eff this up
            if not hasattr(self,'name'): self.name=self.__class__.__name__
            if not hasattr(self,'description'): self.description=self.name
            if not hasattr(self,'force'): self.force=False
            if not hasattr(self,'skip_success_check'): self.skip_success_check=False
        except Exception as e:
            print "Step.__init__: caught %s" % e

    def __setitem__(self,k,v):
        #self.__dict__[k]=v
        super(Step,self).__setitem__(k,v)
        if hasattr(self,k):
            if callable(getattr(self,k)):
                m=getattr(self,k)
                m(v)
        else:
            setattr(self,k,v)

    # update() and setdefault() taken from http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    ########################################################################
    __tablename__='step'


    @classmethod
    def create_table(self, metadata, engine):

        step_table=Table(self.__tablename__, metadata,
                         Column('id',Integer, primary_key=True),
                         Column('name',String, nullable=False, index=True, unique=True),
                         Column('description', String),
                         )
        metadata.create_all(engine)

        sa_properties={'step_runs':relationship(StepRun, backref='step')}
        mapper(Step, step_table, sa_properties)
        return step_table
    


    

    ########################################################################

    # If a step needs more than one line to invoke (eg bowtie: needs to set an environment variable),
    # define the set of commands in a template and set the 'sh_template' attribute to point to the template
    # within the templates/sh_templates subdir).  This routine fetches the template and calls evoque on it, and
    # returns the resulting string.
    # If no sh_template is required, return None.
    def sh_script(self, **kwargs):
        try: sh_template=self.sh_template
        except: return None
            
        template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),"templates","sh_template")
        domain=Domain(template_dir, errors=4)
        template=domain.get_template(sh_template)
        
        vars={}
        vars.update(self)
        vars.update(self.__dict__)
        vars['readset']=self.pipeline.readset # fixme: really? used by some steps, eg mapsplice
        vars['sh_cmd']=self.sh_cmdline() 
        vars['config']=RnaseqGlobals.config
        vars['pipeline']=self.pipeline
        vars['ID']=self.pipeline.ID()
        vars.update(kwargs)

        try: script=template.evoque(vars)
        except NameError as ne: raise ConfigError("%s while processing step '%s'" %(ne,self.name))
        return script

    # use the self.usage formatting string to create the command line that executes the script/program for
    # this step.  Return as a string.  Throws exceptions as die()'s.
    def sh_cmdline(self):
        try:
            usage=self.usage
            if usage==None: usage=''
        except AttributeError:
            usage=''

        # look for exe in path, unless exe is an absolute path
        try:
            if os.path.abspath(self.exe)!=self.exe:
                self.exe=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'programs', self.exe)
        except AttributeError as ae:          # not all steps have self.exe; eg header, footer
            pass


        # expand the usage string, using a built hash (dict):
        h={}
        h.update(self.__dict__)
        try: h.update(self.pipeline[self.name])
        except: pass
        h.update(obj2dict(self))
        ver1=usage % h
       
        # evoque the cmd str:
        domain=Domain(os.getcwd(), errors=4)
        domain.set_template(self.name, src=ver1)
        tmp=domain.get_template(self.name)
        vars={}
        vars.update(self.__dict__)
        vars.update(h)
        vars.update(self.pipeline)
        vars.update(RnaseqGlobals.config)

        try: cmd=tmp.evoque(vars)
        except AttributeError as ae:
            raise ConfigError(ae)
        return cmd


    # entry point to step's sh "presence"; calls appropriate functions, as above.
    def sh_cmd(self, **args):
        echo_part=''
        if 'echo_name' in args and args['echo_name']:
            echo_part="echo step %s 1>&2" % self.name
            
        sh_script=self.sh_script()      # try the templated version first
        if sh_script==None:
            sh_script=self.sh_cmdline()+"\n" # 

        script="\n".join([echo_part,sh_script]) # tried using echo_part+sh_script, got weird '>' -> '&gt;' substitutions

        return script

########################################################################

    def inputs(self):
        try: return re.split("[,\s]+",self.input)
        except: return []

    def outputs(self):
        try: return re.split("[,\s]+",self.output)
        except: return []
    
    def creates(self):
        try: return re.split("[,\s]+",self.create)
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

            try:
                exe_file=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'programs', self.exe)
                exe_mtime=os.stat(exe_file).st_mtime
                if exe_mtime > latest_input:
                    latest_input=exe_mtime
            except OSError as oe:
                raise ConfigError("%s: %s" %(exe_file, oe))

        for output in self.outputs():
            try:
                stat_info=os.stat(output)
                if (stat_info.st_mtime < earliest_output):
                    earliest_output=stat_info.st_mtime
            except OSError as ose:
                return False            # missing/unaccessible outputs definitely constitute not being current

        #print "final: latest_input is %s, earliest_output is %s" % (latest_input, earliest_output)
        return latest_input<earliest_output
    
########################################################################


#print __file__,"checking in"
