#-*-python-*-

import sys, yaml, re, time, os

from warn import *
from dict_like import *
from templated import *
from step import *
from RnaseqGlobals import RnaseqGlobals
import path_helpers

# todo/fixme:
# pipelines should verify that the step list in the .syml file exactly matches
# all the steps found (ie, all present and accounted for, no extras)


class Pipeline(templated, dict_like):
    attrs={'name':None,
           'description':None,
           'type':'pipeline',
           'suffix':'syml',
           'steps':[],
           'readset':None,
           'columns':{'name':'VARCHAR[255]',
                      'description':'TEXT',
                      'status':'VARCHAR[255]'}

           }

    def __init__(self,**args):
        dict_like.__init__(self,**args)
        templated.__init__(self,**args)
        self.type='pipeline'


    def stepWithName(self,stepname):
        for step in self.steps:
            if step.name==stepname: return step 
        return None

    def load(self):
        vars=self.readset.attributes()
        vars.update(RnaseqGlobals.config)
        
        #vars['readset']=self.readset
        vars['readsfile']=self.readset.reads_file # fixme: might want to make reads_file a function, if iterated
        templated.load(self, vars=vars)

        # load steps.  (We're going to replace the current steps field, which holds a string of stepnames,
        # with a list of step objects
        stepnames=re.split('[,\s]+',self.steps)
        steps=[]                   # just to make sure
        for sn in stepnames:
            #print "step %s" % sn
            step=Step(name=sn, pipeline=self)
            
            # load the step's template and self.update with the values:
            try:
                step.load()
            except IOError as ioe:      # IOError??? Where does this generate an IOError?
                raise ConfigError("Unable to load step %s" % sn, ioe)
            step.merge(self.readset)
            # print "pipeline.load: step after merge(readset) is %s" % step

            # add in items from step sections in <pipeline.syml>
            # fixme: self.
            if not self.has_attr(step.name) or self[step.name] == None:
                raise ConfigError("Missing section: '%s' is listed as a step name in %s, but section with that name is absent." % \
                                  (step.name, self.template_file()))
                                  

            try:
                # print "pipeline: self[%s] is\n%s" % (step.name, self[step.name])
                step.update(self[step.name])
                # print "pipeline: step %s is\n%s" %(step.name, step)
            except KeyError as e:
                raise ConfigError("no %s in\n%s" % (step.name, yaml.dump(self.__dict__)))
                
            # print "pipeline: step %s:\n%s" % (step.name, yaml.dump(step))
            
            steps.append(step)
            
        self.steps=steps

        # Check to see that the list of step names and the steps themselves match; dies on errors
        errors=[]
        errors.extend(self.verify_steps(stepnames))
        errors.extend(self.verify_continuity(stepnames))
        errors.extend(self.verify_exes(stepnames))
        if len(errors)>0:
            errors.append("Please link these executables from the %s/bin directory, or make sure they are on the path defined in the config file." \
                          % RnaseqGlobals.conf_value('rnaseq', 'root_dir'))
            raise ConfigError("\n".join(errors))
        
        return self
    
    # return an entire shell script that runs the pipeline
    # warning: this will add a "current" check, which might become out of date if
    # things change between when this script is created and when it is executed.
    def sh_script(self):
        script="#!/bin/sh\n\n"
        check_step=Step(name='check_success', pipeline=self).load()
        prov_step=Step(name='provenance', pipeline=self).load()
        prov_step.cmd='insert'
        prov_step.flags=''
        
        for step in self.steps:
            # put in check_current step:
            # fixme: test this!!!
            if not RnaseqGlobals.option('force'):
                if step.is_current() and not step.force:       # fixme: add --force check, but figure out how to access non-existant options first
                    print "step %s is current, skipping" % step.name
                    continue                # break out instead? fixme: think this through
            
            # actual step
            script+="# %s\n" % step.name
            script+=step.sh_cmd(echo_name=True)
            script+="\n"

            # insert check success step:
            if not ('skip_success_check' in step.attributes() and step.skip_success_check): # god python is annoying at times
                check_step.last_step=step.name
                script+=check_step.sh_cmd()

            # record provenance for outputs:
            for o in set(step.outputs())|set(step.creates()):
                prov_step.output=o
                prov_step.args=" ".join((o, step.exe)) # double (())'s to make it a tuple
                try: 
                    script+=prov_step.sh_cmd()
                except RnaseqException as e:
                    import traceback
                    traceback.print_exc()
                    print "pipeline.sh_script(), step %s: caught e is %s" % (step.name, e)
                    raise e
            script+="\n"

        # record finish:
        prov_step.cmd='update'
        prov_step.args="-p %s --status finished" % self.name
        script+=prov_step.sh_cmd()
        
        return script

    def scriptname(self):
        return path_helpers.sanitize(self.name)+".sh"

    # get the working directory for the pipeline.
    # first ,check to see if the readset defines a working_dir
    # second, see if the pipeline itself defines a pipeline (it shouldn't)
    # each of the first two can be a directory, or a "policy".
    # valid policies include "timestamp" (and nothing else, for the moment)
    # If nothing found, use default found in config file under "default_working_dir"
    def working_dir(self):
        try:
            readset=self.readset
            readsfile=readset.reads_file
            base_dir=os.path.dirname(readsfile)
        except KeyError as ke:
            print "ke is %s" % ke
            raise UserError(ke)

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

        default='rnaseq_'+time.strftime("%d%b%y.%H%M%S")
        return os.path.join(base_dir, default)


    #  check to see that all defined steps are listed, and vice verse:
    def verify_steps(self, stepnames):
        errors=[]
        a=set(stepnames)
        b=set(self.attributes().keys())-set(self.attrs.keys()) # whee! set subtraction!
        if a==b: return errors            # set equality! we just love over-ridden operators
        # fixme: the above is really fragile, and might break if Pipeline inherits from anything else using dict_like (or other classes?)

        name_no_step=a-b                # more set subtraction!
        if len(name_no_step)>0:
            errors.append("The following steps were listed as part of %s, but no defining section was found: %s" % (self.name, ", ".join(list(name_no_step))))
            
        step_no_name=b-a                # more set subtraction!
        if len(step_no_name)>0:
            errors.append("The following steps were defined as part of %s, but not listed: %s" % (self.name, ", ".join(list(step_no_name))))
        
        return errors


    # check to see that all inputs and outputs connect up correctly (fixme: describe this more clearly)
    def verify_continuity(self, stepnames):
        step=self.stepWithName(stepnames[0])
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
        for sn in stepnames[1:]:        # skip first
            step=self.stepWithName(sn)
            for input in step.inputs():
                if input not in dataset2stepname and not os.path.exists(input):
                    errors.append("input %s (in step '%s') is not produced by any previous step and does not currently exist" % (input, step.name))
            for output in step.outputs():
                dataset2stepname[output]=step.name
            for created in step.creates():
                dataset2stepname[created]=step.name

        return errors
            

    def verify_exes(self, stepnames):
        dirs=RnaseqGlobals.conf_value('rnaseq', 'path').split(":")
        dirs.extend([os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),'bin')])
            
        errors=[]
        for stepname in stepnames:
            step=self.stepWithName(stepname)
            for d in dirs:
                try:
                    path=os.path.join(d,step.exe)
                except AttributeError as ae:
                    break
                if os.access(path, os.X_OK) and not os.path.isdir(path): break
                if 'interpreter' in step.attributes() and os.access(path, os.R_OK): break
            else:                       # gets executed if for loop exits normally
                errors.append("Missing executable in %s: %s" %(stepname, step.exe))

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
        vars=self.attributes()
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
