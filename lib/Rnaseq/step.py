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
from evoque_helpers import evoque_template

class Step(dict):                     # was Step(templated)
    defaults={}
    required_attrs=[]
    
    def __init__(self,*args,**kwargs):
        # set defaults:
        self.name=self.__class__.__name__
        self.description=self.name
        self.force=False
        self.skip_success_check=False
        self.is_prov_step=False
        
        for k,v in self.defaults.items():
            setattr(self,k,v)

        for k,v in kwargs.items():
            try: setattr(self,k,v)      # something in alchemy can eff this up
            except Exception as e: print "templated.__init__: caught %s" % e

    def missing_required_attrs(self):
        missing=[]
        #print "%s: required are %s"  % (self.name, self.required_attrs)
        for attr in self.required_attrs:
            if not hasattr(self, attr):
                missing.append(attr)
            else:
                pass
                #print "%s.%s is %s" % (self.name, attr, getattr(self,attr))
        return missing

    ########################################################################

    def __setitem__(self,k,v):
        super(Step,self).__setitem__(k,v) # call dict.__setitem__()
        super(Step,self).__setattr__(k,v)

    def __setattr__(self,attr,value):
        super(Step,self).__setattr__(attr,value) # call dict.__setattr__()
        super(Step,self).__setitem__(attr,value)

    # update() and setdefault() taken from http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                if key not in self: self[key] = other[key]
        for key in kwargs:
            if key not in self: self[key] = kwargs[key]

    def update_o(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    ########################################################################

    def usage(self, context):
        raise ProgrammerGoof("step class '%s' does not define usage(self,context)" % self.__class__.__name__)

    def outputs(self):
        raise ProgrammerGoof("step class '%s' does not define outputs(self)" % self.__class__.__name__)

    def paired_end(self):
        try: return self.pipeline.readset.paired_end
        except AttributeError: return False

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
            echo_part="\n# step %s:\n" % self.name
            echo_part+="echo step %s 1>&2" % self.name
        else:
            echo_part=''
            
        try: usage=self.usage(context) 
        except KeyError as ke:
            raise ConfigError("missing config item '%s'" % ke)

        
        # check for missing attrs after calling step.usage()
        missing_attrs=self.missing_required_attrs()
        if len(missing_attrs) > 0:
            raise ConfigError("step %s: missing attributes: %s" % (self.name, ', '.join(missing_attrs)))


        vars={}
        vars.update(self.__dict__)
        vars.update(self.pipeline.readset)
        if not self.is_prov_step:
            vars.update(self.pipeline[self.name])
            vars['inputs']=context.inputs[self.name]
            vars['outputs']=context.outputs[self.name]

        vars['pipeline']=self.pipeline
        vars['pipeline_run_id']=context.pipeline_run_id
        #vars['step_run_id']=context.step_runs[self.name].id
        #vars['next_step_run_id']=context.step_runs[self.pipeline.step_after(step.name)].id
        vars['config']=RnaseqGlobals.config
        vars['readset']=self.pipeline.readset

        # need to add shell variables for 'set': (in cufflinks.s_?.sh scripts)
        # currently root_dir, programs, reads_file, ID, format, readlen
        # but really, the pipeline should specify these?
        # or only things that are truly universal
        vars['root_dir']=RnaseqGlobals.root_dir()

        # add readset exports:
        readset=self.pipeline.readset
        for attr in readset.exports:
            try: vars[attr]=getattr(readset, attr)
            except AttributeError:
                vars[attr]=''
                #warn("%s.sh_script: no '%s' readset attribute!" % (self.name, attr))

        # add self.exports:
        try: export_list=self.exports
        except: export_list=[]
        for attr in export_list:
            vars[attr]=getattr(self,attr)

        try: script_part=evoque_template(usage, vars)
        except Exception as e: raise ConfigError("step %s: %s" % (self.name, e))
        
        script="\n".join([echo_part,script_part]) # tried using echo_part+sh_script, got weird '>' -> '&gt;' substitutions

        return script

    ########################################################################

    # get the input list from the pipeline's context (which means pipeline.convert_io() must have completed)
    def input_list(self):
        return self.pipeline.context.inputs[self.name] # barfing on no context

    def input_list_expanded(self):
        l=[evoque_template(x, self, self.pipeline.readset) for x in self.input_list()]
        return l

    def output_list(self, *args):
        raise ProgrammerGoof("pipeline %s - step '%s' does not define it's outputs" % (self.pipeline.name, self.name))

    def output_list_expanded(self):
        l=[evoque_template(x, self, self.pipeline.readset) for x in self.output_list()]
        return l


    ########################################################################
    # current: return true if all of the step's outputs are older than all
    # of the steps inputs AND the step's exe:
    def is_current(self):
        if self.force: return False
        latest_input=0
        earliest_output=time.time()
        try: debug=os.environ['DEBUG']
        except: debug=False
        
        for input in self.input_list_expanded():
            if debug: print "%s: input checking %s" % (self.name, input)
            
            try:
                mtime=os.stat(input).st_mtime
            except OSError as ose:
                if debug:
                    print "%s: returning false due to failed stat: %s" % (self.name, ose)
                return False            # missing/unaccessible inputs constitute not being current
            
            if mtime > latest_input:
                latest_input=mtime


        for output in self.output_list_expanded():
            if debug: print "%s: checking output %s" % (self.name, output)
            try:
                stat_info=os.stat(output)
                if (stat_info.st_mtime < earliest_output):
                    earliest_output=stat_info.st_mtime
            except OSError as ose:
                if debug:
                    print "%s: returning false on %s" % (self.name, ose)
                return False            # missing/unaccessible outputs definitely constitute not being current

        if debug:
            print "%s final: latest_input is %s, earliest_output is %s" % (self.name, latest_input, earliest_output)
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
        


#print __file__,"checking in"
