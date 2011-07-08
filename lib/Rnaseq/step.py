#-*-python-*-

import yaml, time, re
from RnaseqGlobals import RnaseqGlobals
from warn import *
from Rnaseq import *
from step_run import *

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from hash_helpers import obj2dict
from path_helpers import exists_on_path

class Step(dict):                     # was Step(templated)
    def __init__(self,*args,**kwargs):
        # set defaults:
        self.name=self.__class__.__name__
        self.description=self.name
        self.force=False
        self.skip_success_check=False

        for k,v in kwargs.items():
            try: setattr(self,k,v)      # something in alchemy can eff this up
            except Exception as e: print "templated.__init__: caught %s" % e

#        print "__init__: %s is %s" % (self.name, yaml.dump(self))


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


    # entry point to step's sh "presence"; calls appropriate functions, as above.
    def sh_script(self, context, **args):

        if 'echo_name' in args and args['echo_name']:
            echo_part="echo step %s 1>&2" % self.name
        else:
            echo_part=''
            
        sh_script=self.usage(context)

        domain=Domain(os.getcwd(), errors=4) # we actually don't care about the first arg
        domain.set_template(self.name, src=sh_script)
        tmp=domain.get_template(self.name)

        vars={}
        vars.update(self.__dict__)               # fixme: this does nothing, apparently
        vars.update(context)
        vars['pipeline']=self.pipeline
        vars['config']=RnaseqGlobals.config
        vars['readset']=self.pipeline.readset

        # need to add shell variables for 'set': (in cufflinks.s_?.sh scripts)
        # currently root_dir, programs, reads_file, ID, format, readlen
        # but really, the pipeline should specify these?
        # or only things that are truly universal
        vars['root_dir']=RnaseqGlobals.root_dir()
        vars['programs']=RnaseqGlobals.root_dir()+'/programs'
        vars['reads_file']=self.pipeline.readset.reads_file
        vars['ID']=self.pipeline.readset.ID
        vars['working_dir']=self.pipeline.readset.working_dir

        script=tmp.evoque(vars)
        script="\n".join([echo_part,script]) # tried using echo_part+sh_script, got weird '>' -> '&gt;' substitutions

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

    # return True of False depending on if step.exe can be found on the
    # global path, or if it's an interpreted step, if the interpreter
    # can be found on the same path and the script is in the programs directory
    
    def verify_exe(self):
        if not hasattr(self,'exe'): return True

        dir_list=RnaseqGlobals.conf_value('rnaseq', 'path').split(":")
        dir_list.extend([os.path.join(RnaseqGlobals.root_dir(),'programs')])

        if exists_on_path(self.exe, dir_list, os.X_OK): return True
        
        # didn't find executable directly, see if there's an interpreter:
        if hasattr(self,'interpreter'):
            return exists_on_path(self.interpreter, dir_list, os.X_OK) and \
                   exists_on_path(self.exe, dir_list, os.R_OK)

        # couldn't find self.exe, no self.interpreter:
        return False
        

    ########################################################################
    ########################################################################
    # Dead code
    dead_code='''

    # If a step needs more than one line to invoke (eg bowtie: needs to set an environment variable),
    # define the set of commands in a template and set the 'sh_template' attribute to point to the template
    # within the templates/sh_templates subdir).  This routine fetches the template and calls evoque on it, and
    # returns the resulting string.
    # If no sh_template is required, return None.
    def sh_script_old(self, **kwargs):
        try: sh_template=self.sh_template
        except: return None
        
        template_dir=os.path.join(RnaseqGlobals.root_dir(),"templates","sh_template")
        domain=Domain(template_dir, errors=4)
        template=domain.get_template(sh_template)
        
        vars={}
        vars.update(self.__dict__)
        vars.update(self)
        try: vars.update(self.pipeline[self.name])
        except: pass

        #vars['readset']=self.pipeline.readset # fixme: really? used by some steps, eg mapsplice
        vars['sh_cmd']=self.sh_cmdline()
        vars['config']=RnaseqGlobals.config
        vars['ID']=self.pipeline.ID()

        try:
            vars.update(self.pipeline.step_exports)
        except AttributeError as ae:
            pass

        vars.update(kwargs)

        try:
            script=template.evoque(vars)
        except NameError as ne: 
            #print "%s.sh_script() not ok (ne=%s)" % (self.name, ne)
            raise ConfigError("%s while processing step '%s'" %(ne,self.name))

        return script

    # use the self.usage formatting string to create the command line that executes the script/program for
    # this step.  Return as a string.  Throws exceptions as die()'s.
    def sh_cmdline_old(self):
        usage=self.usage()


        # evoque the cmd str:
        domain=Domain(os.getcwd(), errors=4) # we actually don't care about the first arg
        domain.set_template(self.name, src=usage)
        tmp=domain.get_template(self.name)
        vars={}
        vars.update(self.__dict__)
#        vars.update(self.pipeline)
        vars.update(RnaseqGlobals.config)

        try: vars.update(self.pipeline[self.name])
        except: pass

        try: vars.update(self.pipeline.step_exports) # fixme: still need this?
        except: pass

        try: cmd=tmp.evoque(vars)
        except AttributeError as ae:
            raise ConfigError(ae)
        return cmd


    # 
#     def __setitem__(self,k,v):
#         super(Step,self).__setitem__(k,v) # call dict.__setitem__()
#         if hasattr(self,k):
#             if callable(getattr(self,k)):
#                 m=getattr(self,k)
#                 m(v)
#         else:
#             setattr(self,k,v)

#     # update() and setdefault() taken from http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
#     def update(self, *args, **kwargs):
#         if args:
#             if len(args) > 1:
#                 raise TypeError("update expected at most 1 arguments, got %d" % len(args))
#             other = dict(args[0])
#             for key in other:
#                 self[key] = other[key]
#         for key in kwargs:
#             self[key] = kwargs[key]

#     def setdefault(self, key, value=None):
#         if key not in self:
#             self[key] = value
#         return self[key]


#     def __setattr__(self,attr,value):
#         super(Step,self).__setattr__(attr,value) # call dict.__setattr__()
#         self.__dict__[attr]=value


    '''


#print __file__,"checking in"
