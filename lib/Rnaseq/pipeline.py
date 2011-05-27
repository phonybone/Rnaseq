#-*-python-*-

# step_object version

import sys, yaml, re, time, os, re

from step import *
from warn import *
from dict_like import *
from templated import *
from RnaseqGlobals import RnaseqGlobals
from pipeline_run import *
from step_run import *
import path_helpers
from sqlalchemy import *
from sqlalchemy.orm import mapper
from hash_helpers import obj2dict

class Pipeline(templated):
    def __init__(self,*args,**kwargs):
        templated.__init__(self,*args,**kwargs)
        self.type='pipeline'
        self.suffix='syml'
        self.steps=[]
        self._ID=None

    wd_time_format="%d%b%y.%H%M%S"

    def __str__(self):
        return "%s" % self.name

    ########################################################################

    __tablename__='pipeline'
        
    @classmethod
    def create_table(self, metadata, engine):
        pipeline_table=Table(self.__tablename__, metadata,
                             Column('id', Integer, primary_key=True, autoincrement=True),
                             Column('name', String, nullable=False, index=True, unique=True),
                             Column('description', String),
                             )
        metadata.create_all(engine)

        sa_properties={'pipeline_runs':relationship(PipelineRun, backref='pipeline'),
                       }
        mapper(Pipeline, pipeline_table, sa_properties)
        return pipeline_table
    

    ########################################################################

    # return the step with the given step name, or None if not found:
    def stepWithName(self,stepname):
        for step in self.steps:
            if step.name==stepname: return step 
        return None

    # return the step after the given step (by name), or None if not found:
    def stepAfter(self,stepname):
        prev_step=self.steps[0]
        for step in self.steps[1:]:
            if prev_step.name==stepname: return step
            prev_step=step
        return None

    # read in the (s)yml file that defines the pipeline, passing the contents the evoque as needed.
    # load in all of the steps (via a similar mechanism), creating a list in self.steps
    # raise errors as needed (mostly ConfigError's)
    # returns self
    def load(self):
        vars={}
        if hasattr(self,'dict'): vars.update(self.dict)
        if hasattr(self, 'readset'): vars.update(self.readset)
        vars.update(RnaseqGlobals.config)
        vars['ID']=self.ID()
        ev=evoque_dict()
        ev.update(vars)
        templated.load(self, vars=ev, final=False)
        
        # load steps.  (We're going to replace the current steps field, which holds a string of stepnames,
        # with a list of step objects.
        # fixme: explicitly add header and footer steps; 

        try:
            self.stepnames=re.split('[,\s]+',self['stepnames'])
        except AttributeError as ae:
            raise ConfigError("pipeline %s does not define stepnames" % self.name)
            
        self.steps=[]                   # resest, just in case
        for sn in self.stepnames:
            step=Step(name=sn, pipeline=self)
            assert step.pipeline==self
            # load the step's template and self.update with the values:
            try:
                vars={}
                vars.update(self.dict)
                vars.update(RnaseqGlobals.config)
                vars['ID']=self.ID()
                step.load(vars=vars)
            except IOError as ioe:      # IOError??? Where does this generate an IOError?
                raise ConfigError("Unable to load step %s" % sn, ioe)
            step.merge(self.readset)

            # add in items from step sections in <pipeline.syml>
            try:
                step_hash=self[step.name]
            except Exception as e:
                raise ConfigError("Missing section: '%s' is listed as a step name in %s, but section with that name is absent." % \
                                  (step.name, self.template_file()))
                                  
            #print "%s: step_hash is %s" % (step.name, step_hash)

            try:
                step.update(step_hash)
            except KeyError as e:
                raise ConfigError("no %s in\n%s" % (step.name, yaml.dump(self.__dict__)))

            self.steps.append(step)
            

        # Check to see that the list of step names and the steps themselves match; dies on errors
        errors=[]
        errors.extend(self.verify_steps())
        errors.extend(self.verify_continuity())
        errors.extend(self.verify_exes())
        if len(errors)>0:
            raise ConfigError("\n".join(errors))
        
        return self


    def load_steps(self):
        self.load_template()

        try:
            self.stepnames=re.split('[,\s]+',self['stepnames'])
        except AttributeError as ae:
            raise ConfigError("pipeline %s does not define stepnames" % self.name)
        for stepname in self.stepnames:
            step=self.new_step(stepname)

            # fix any ${} vars in self[stepname]: what a hack
            for k,v in self[stepname].items():
                if type(v)!=type('str'): continue
                if re.search('\$\{',v):
                    vars=evoque_dict()
                    vars.update(step.__dict__)
                    vars.update(obj2dict(step))
                    domain=Domain(os.getcwd())
                    domain.set_template(k, src=v)
                    tmpl=domain.get_template(k)
                    v=tmpl.evoque(vars)
                    self[stepname][k]=v

            step.update(self[stepname])
            self.steps.append(step)
        return self

    def load_template(self):
        vars={}
        vars.update(self.dict)
        #vars.update(self.readset)       # why not?
        vars.update(RnaseqGlobals.config)
        vars['ID']=self.ID()

        ev=evoque_dict()
        ev.update(vars)
        templated.load(self, vars=ev, final=False)
        


    ########################################################################
    # Write the pipeline's shell script to disk.
    # Returns full path of script name.
    def write_sh_script(self, **kwargs):
        script=self.sh_script(**kwargs)
        script_filename=os.path.join(self.working_dir(), self.scriptname())
        try:
            os.makedirs(self.working_dir())
        except OSError:
            pass                    # already exists, that's ok (fixme: could be permissions error)
        with open(script_filename, "w") as f:
            f.write(script)
            print "%s written" % script_filename
        return script_filename




    # return an entire shell script that runs the pipeline
    def sh_script(self, **kwargs):
        
        script="#!/bin/sh\n\n"

        try:
            pipeline_run=kwargs['pipeline_run']
            step_runs=kwargs['step_runs']
            include_provenance=True
        except KeyError:
            include_provenance=False
            
        # create auxillary steps:
        if include_provenance:
            pipeline_start=self.new_step('pipeline_start',pipelinerun_id=pipeline_run.id)
            pipeline_start.next_steprun_id=step_runs[self.steps[0].name].id
            mid_step=self.new_step('mid_step', pipeline_run_id=pipeline_run.id)
            pipeline_end=self.new_step('pipeline_end', pipelinerun_id=pipeline_run.id)
            script+=pipeline_start.sh_cmd()

        errors=[]
        for step in self.steps:
            try:
                if step.skip_step: continue  # in a try block in case step.skip doesn't even exist
            except: pass
                
            
            # actual step
            script+="# %s\n" % step.name

            try: step_script=step.sh_cmd(echo_name=True)
            except Exception as e: errors.append("%s: %s" % (step.name,str(e)))

            script+=step_script
            script+="\n"

            # insert check success step:
            if include_provenance:
                try: skip_check=step['skip_success_check'] 
                except: skip_check=False
                if not skip_check:
                    step_run=step_runs[step.name]
                    step_run.cmd=step_script
                    mid_step.stepname=step.name
                    mid_step.steprun_id=step_run.id
                    next_step=self.stepAfter(step.name)
                    try:
                        mid_step.next_steprun_id=step_runs[self.stepAfter(step.name).name].id # sheesh
                    except:
                        mid_step.next_steprun_id=0
                    script+=mid_step.sh_cmd()

            if not RnaseqGlobals.conf_value('silent'):
                print "step %s added" % step.name

        if len(errors)>0:
            raise ConfigError("\n".join(errors))
            
        # record finish:
        if include_provenance:
            script+=pipeline_end.sh_cmd()

        return script

    def scriptname(self):
        reads_file_root=os.path.splitext(os.path.basename(self.readset['reads_file']))[0]
        return path_helpers.sanitize(self.name+'.'+reads_file_root)+".sh"

    # get the working directory for the pipeline.
    # first ,check to see if the readset defines a working_dir
    # second, see if the pipeline itself defines a pipeline (it shouldn't)
    # each of the first two can be a directory, or a "policy".
    # valid policies include "timestamp" (and nothing else, for the moment)
    # If nothing found, use default found in config file under "default_working_dir"
    def working_dir(self,*args):
        try: self['working_dir']=args[0]
        except IndexError: pass

        
        # (try to) get the base dir from the readset:
        try:
            readset=self.readset
            readsfile=readset['reads_file']
            base_dir=os.path.dirname(readsfile)
        except KeyError as ke:
            raise UserError("Missing key: "+ke) # fixme: UserError?  really?

        # see if self['working_dir'] is defined
        try:
            wd=os.path.join(base_dir, self['working_dir'])
            return wd
        except KeyError as ie:
            pass

        # see if the readset defines a working_dir:
        try:
            wd=os.path.join(base_dir, readset['working_dir'])
            return wd
        except KeyError as ie:
            pass

        # nothing found: generate a working_dir from a timestamp:
        default='rnaseq_'+time.strftime(self.wd_time_format)
        return os.path.join(base_dir, default)


    # Determine the path of the working reads file.  Path will be
    # a combination of a working_directory and the basename of the
    # readsfile.  Final value will depend on whether the reads file
    # or the specified working directory are relative or absolute.
    # fixme: why doesn't this call self.working_dir() anywhere?
    def ID(self):
        try: reads_file=self.readset['reads_file']
        except KeyError: return '${ID}'

        if re.search('[\*\?]', reads_file):
            raise ProgrammerGoof("%s contains glob chars; need to expand readset.path_iterator()" % reads_file)

        # try a few different things to get the working directory:
        try:
            wd=self.readset['working_dir']
            if (wd=='wd_timestamp'): wd='rnaseq_'+time.strftime(self.wd_time_format)
            #print "1. wd is %s" % wd
            
        except KeyError:
            try:
                wd=self['working_dir']
                if (wd=='wd_timestamp'): wd='rnaseq_'+time.strftime(self.wd_time_format)
                #print "2. wd is %s" % wd

            except KeyError:
                if os.path.isabs(reads_file):
                    wd=os.path.dirname(reads_file)
                    #print "3. wd is %s" % wd
                elif RnaseqGlobals.conf_value('rnaseq','wd_timestamp') or \
                     ('wd_timestamp' in self.dict and \
                      self.dict['wd_timestamp']): # -and isn't set to False
                    wd='rnaseq_'+time.strftime(self.wd_time_format)
                    #print "4. wd is %s" % wd
                
                else:
                    wd=os.getcwd()
                    #print "5. wd is %s" % wd

        if os.path.isabs(wd):
            id=os.path.join(wd,os.path.basename(reads_file)) #
            #print "6. id is %s" % id
        elif os.path.isabs(reads_file):
            id=os.path.join(os.path.dirname(reads_file), wd, os.path.basename(reads_file))
            #print "7. id is %s" % id
        else:
            id=os.path.join(os.getcwd(), wd, os.path.basename(reads_file))
            #print "8. id is %s" % id

        #self._ID=id
        #print "ID() returning %s" % id
        return id
        


    #  check to see that all defined steps are listed, and vice verse:
    def verify_steps(self):
        errors=[]
        a=set(self.stepnames)
        b=set(s.name for s in self.steps)
        
        if a==b: return errors            # set equality! we just love over-ridden operators

        name_no_step=a-b                # more set subtraction!
        if len(name_no_step)>0:
            errors.append("The following steps were listed as part of %s, but no defining section was found: %s" % (self.name, ", ".join(list(name_no_step))))
            
        step_no_name=b-a                # more set subtraction!
        if len(step_no_name)>0:
            errors.append("The following steps were defined as part of %s, but not listed: %s" % (self.name, ", ".join(list(step_no_name))))
        
        return errors


    # check to see that all inputs and outputs connect up correctly and are accounted for
    # outputs also include files defined by "create"
    def verify_continuity(self):
        step=self.steps[0]
        errors=[]
        dataset2stepname={}
        
        # first step: check that inputs exist on fs, prime dataset2stepname:
        for input in step.inputs():
            if not os.path.exists(input):
                errors.append("missing inputs for %s: %s" % (step.name, input))
        for output in step.outputs():
            dataset2stepname[output]=step.name
        for created in step.creates():
            dataset2stepname[created]=step.name
            print "added %s" % created

        # subsequent steps: check inputs exist in dataset2stepname, add outputs to dataset2stepname:
        for step in self.steps[1:]:        # skip first
            for input in step.inputs():
                if input not in dataset2stepname and not os.path.exists(input):
                    errors.append("input %s (in step '%s') is not produced by any previous step and does not currently exist" % (input, step.name))
            for output in step.outputs():
                dataset2stepname[output]=step.name
            for created in step.creates():
                dataset2stepname[created]=step.name

        return errors
            

    def verify_exes(self):
        dirs=RnaseqGlobals.conf_value('rnaseq', 'path').split(":")
        dirs.extend([os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),'programs')])
            
        errors=[]
        for step in self.steps:
            for d in dirs:
                try:
                    path=os.path.join(d,step.exe) # how does this generate an AttributeError??? on step.exe???
                except AttributeError as ae:
                    break

                if os.access(path, os.X_OK) and not os.path.isdir(path): break
                if 'interpreter' in step.dict and os.access(path, os.R_OK): break
                try: intr=step.interpreter
                except: intr=None
            else:                       # gets executed if for loop exits normally
                errors.append("Missing executable in %s: %s" %(step.name, step.exe))

        if len(errors)>0:
            errors.append("Please link these executables from the %s/programs directory, or make sure they are on the path defined in the config file." \
                          % RnaseqGlobals.conf_value('rnaseq', 'root_dir'))
            

        return errors

    ########################################################################


    def out_filename(self):
        return path_helpers.sanitize(os.path.join(self.working_dir(), "%s.out" % self.name))
    def err_filename(self):
        return path_helpers.sanitize(os.path.join(self.working_dir(), "%s.err" % self.name))
        

    # create the qsub script using a template:
    def qsub_script(self, script_filename, out_filename=None, err_filename=None):
        if out_filename==None: out_filename=self.out_filename()
        if err_filename==None: err_filename=self.err_filename()
        qsub=templated(name='qsub', type='sh_template', suffix='tmpl')
        vars={}
        vars.update(self.dict)
        vars['name']=path_helpers.sanitize(self.name)
        vars['cmd']=script_filename
        vars['out_filename']=out_filename
        vars['err_filename']=err_filename
        qsub_script=qsub.eval_tmpl(vars=vars)

        qsub_script_file=path_helpers.sanitize(os.path.join(self.working_dir(), "%s.qsub" % self.name))
        f=open(qsub_script_file,"w")
        f.write(qsub_script)
        f.close()
        warn("%s written" % qsub_script_file)
        return qsub_script_file

    
    ########################################################################

    # lookup self in db; if not found, store.  Same for all steps.
    def store_db(self):
        session=RnaseqGlobals.get_session()
        other_self=session.query(Pipeline).filter_by(name=self.name).first()
        if other_self==None:
            session.add(self)
        else:
            self.id=other_self.id

        session.commit()
        return self
        

########################################################################

    def new_step(self, stepname, **kwargs):
        try:
            mod=__import__('Rnaseq.steps.%s' % stepname)
        except ImportError as ie:
            raise ConfigError("error loading step %s: %s" % (stepname, str(ie)))
        
        mod=getattr(mod,"steps")

        try:
            mod=getattr(mod,stepname)
            kls=getattr(mod,stepname)            
        except AttributeError as ae:
            raise ConfigError("step %s not defined: "+str(ae))

        kwargs['pipeline']=self
        step=kls(**kwargs)
        return step


    # return a tuple containing a pipeline_run object and a dict of step_run objects (keyed by step name):
    def make_run_objects(self, session):
        self.store_db()
        
        # create the pipeline_run object:
        pipeline_run=PipelineRun()
        pipeline_run=PipelineRun(pipeline_id=self.id, status='standby', input_file=self.readset['reads_file'])
        session.add(pipeline_run)
        session.commit()                # we need the pipelinerun_id below

        # create step_run objects:
        step_runs={}
        for step in self.steps:
            step_run=StepRun(step_name=step.name, pipeline_run_id=pipeline_run.id, status='standby')
            for output in step.outputs():
                step_run.file_outputs.append(FileOutput(path=output))

            if step.skip_step:               # as set by self.set_steps_current()
                print "step %s is current, skipping" % step.name
                step_run.status='skipped'

            session.add(step_run)
            step_runs[step.name]=step_run
        session.commit()                # we need the pipelinerun_id below

        return (pipeline_run, step_runs)


    # for each step, set an attribute 'skip' indicating whether or not to skip the step when creating the sh script:
    def set_steps_current(self, global_force=False):
        force_rest=False
        for step in self.steps:
            skip_step=not (global_force or step.force or force_rest) and step.is_current()
            #print "%s: skip_step is %s" % (step.name, skip_step)
            setattr(step, 'skip', skip_step)

            # once one step is out of date, all following steps will be, too:
            if not step.skip_step: force_rest=True

    




#print "%s checking in: Pipeline.__name__ is %s" % (__file__,Pipeline.__name__)
