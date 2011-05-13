#-*-python-*-

# step_object version

import sys, yaml, re, time, os

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

        sa_properties={'pipeline_runs':relationship(PipelineRun, backref='pipeline')}
        mapper(Pipeline, pipeline_table, sa_properties)
        return pipeline_table
    

    ########################################################################

    def stepWithName(self,stepname):
        for step in self.steps:
            if step.name==stepname: return step 
        return None

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
        vars.update(self.dict)
        vars.update(self.readset)
        vars.update(RnaseqGlobals.config)
        
        #vars['readsfile']=self.readset.reads_file # fixme: might want to make reads_file a function, if iterated
        vars['ID']=self.ID()
        #vars['align_suffix']=RnaseqGlobals.conf_value('rnaseq','align_suffix') # fixme: this really, really shouldn't be here
        #vars['fq_cmd']=RnaseqGlobals.conf_value('rnaseq','fq_cmd') # fixme: this shouldn't be here either
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
            self.steps.append(step)

    def load_template(self):
        vars={}
        vars.update(self.dict)
        #vars.update(self.readset)
        vars.update(RnaseqGlobals.config)
        vars['ID']=self.ID()

        ev=evoque_dict()
        ev.update(vars)
        templated.load(self, vars=ev, final=False)
        


    # return an entire shell script that runs the pipeline
    # warning: this will add a "current" check, which might become out of date if
    # things change between when this script is created and when it is executed.
    def sh_script(self):
        
        script="#!/bin/sh\n\n"

        session=RnaseqGlobals.get_session()
        self.store_db();                # insure self.id exists
        pipeline_run=PipelineRun(pipeline_id=self.id, status='standby')
        session.add(pipeline_run)
        session.commit()                # we need the pipelinerun_id below

        # create step_run objects:
        step_runs={}
        for step in self.steps:
            step_run=StepRun(step_id=step.id, pipeline_run_id=pipeline_run.id, status='standby')
            session.add(step_run)
            step_runs[step.name]=step_run
        session.commit()                # we need the pipelinerun_id below
        
        # create auxillary steps:
        pipeline_start=Step(name='pipeline_start', pipeline=self, pipelinerun_id=pipeline_run.id).load()
        pipeline_start.next_steprun_id=step_runs[self.steps[0].name].id
        mid_step=Step(name='mid_step', pipeline=self, pipeline_run_id=pipeline_run.id).load()
        pipeline_end=Step(name='pipeline_end', pipeline=self, pipelinerun_id=pipeline_run.id).load()

        script+=pipeline_start.sh_cmd()

        last_stepname=self.steps[-1].name
        current_flag=True               # once one step isn't current, the rest aren't either
        for step in self.steps:
            # put in check_current step:
            # fixme: test this!!!
            if not RnaseqGlobals.conf_value('force') and current_flag:
                if step.is_current() and not step.force:
                    print "step %s is current, skipping" % step.name
                    continue
                else:
                    current_flag=False
            
            # actual step
            script+="# %s\n" % step.name
            step_script=step.sh_cmd(echo_name=True)
            script+=step_script
            script+="\n"

            # insert check success step:
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

            script+="\n"
            print "step %s added" % step.name
            
        session.commit()                # to store updated step_run objects
        
        # record finish:
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
    def working_dir(self):
        try:
            readset=self.readset
            readsfile=readset['reads_file']
            base_dir=os.path.dirname(readsfile)
        except KeyError as ke:
            raise UserError("Missing key: "+ke)

        try:
            wd=os.path.join(base_dir, self['working_dir'])
            return wd
        except KeyError as ie:
            pass

        try:
            wd=os.path.join(base_dir, readset['working_dir'])
            return wd
        except KeyError as ie:
            pass

        default='rnaseq_'+time.strftime(self.wd_time_format)
        return os.path.join(base_dir, default)


    # Determine the path of the working reads file.  Path will be
    # a combination of a working_directory and the basename of the
    # readsfile.  Final value will depend on whether the reads file
    # or the specified working directory are relative or absolute.
    # fixme: why doesn't this call self.working_dir() anywhere?
    def ID(self):
        try: reads_file=self.readset['reads_file']
        except: return '${ID}'
        
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
        

    def write_qsub_script(self, script_filename, out_filename=None, err_filename=None):
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

        for step in self.steps:
            other_step=session.query(Step).filter_by(name=step.name).first()
            if other_step == None:
                session.add(step)
            else:
                step.id=other_step.id

        session.commit()
        return self
        

########################################################################

    def new_step(self, stepname, **kwargs):
        mod=__import__('Rnaseq.steps.%s' % stepname)
        mod=getattr(mod,"steps")
        mod=getattr(mod,stepname)
        kls=getattr(mod,stepname)
        step=kls(kwargs)
        return step


#print "%s checking in: Pipeline.__name__ is %s" % (__file__,Pipeline.__name__)
