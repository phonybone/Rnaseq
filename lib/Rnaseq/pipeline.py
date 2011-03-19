#-*-python-*-

import sys, yaml, re, time, os

from warn import *
from dict_like import *
from templated import *
from step import *
import Rnaseq

# todo/fixme:
# pipelines should verify that the step list in the .syml file exactly matches
# all the steps found (ie, all present and accounted for, no extras)


class Pipeline(dict_like, templated):
    attrs={'name':None,
           'description':None,
           'type':'pipeline',
           'steps':[],
           'readset':None,
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
        vars.update(Rnaseq.Rnaseq.config)
        
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
            except IOError as ioe:
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
        self.verifySteps(stepnames)

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
            if (step.is_current() and not step.force):
                print "%s is current, skipping" % step.name
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
            for o in step.outputs():
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
            print "%s: done" % step.name

        # record finish:
        prov_step.cmd='update'
        prov_step.args="-p %s\" --status finished" % self.name
        script+=prov_step.sh_cmd()
        
        return script

    # return an entire shell script that runs the pipeline
    def sh_script_old(self):
        script="#!/bin/sh\n\n"
        
        for step in self.steps:
            script+="# %s\n" % step.name
            script+=step.sh_cmd(echo_name=True)
            script+="\n"

            # insert check success step:
            check_step=Step(name='check_success', pipeline=self).load()
            check_step.last_step=step.name
            try:
                check_block=check_step.sh_cmd()
                script+=check_block
            except TypeError as te:
                print "Unexpected type error %s" % yaml.dump(te)
                for thing in sys.exc_info():
                    print "thing is %s" % thing
                raise te
        return script

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
    def verifySteps(self, stepnames):
        a=set(stepnames)
        b=set(self.attributes().keys())-set(self.attrs.keys()) # whee! set subtraction!
        if a==b: return True            # set equality! we just love over-ridden operators

        msg='Config Error: '
        name_no_step=a-b                # more set subtraction!
        if len(name_no_step)>0:
            msg+="The following steps were listed as part of %s, but no defining section was found: %s" % (self.name, ", ".join(list(name_no_step)))
            
        step_no_name=b-a                # more set subtraction!
        if len(step_no_name)>0:
            msg+="The following steps were defined as part of %s, but not listed: %s" % (self.name, ", ".join(list(step_no_name)))
        
        raise ConfigError(msg)



#print __file__,"checking in; Rnaseq.__file__ is %s" % Rnaseq.__file__
    
