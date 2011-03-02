#-*-python-*-

import yaml
import re

from warn import warn,die
from dict_like import *
from templated import *
from step import *

class Pipeline(dict_like, templated):
    attrs={'name':None,
           'type':'pipeline',
           'steps':[],
           'readset':None,
           }

    def __init__(self,**args):
        dict_like.__init__(self,**args)
        templated.__init__(self,**args)
        self.type='pipeline'


    def stepByName(self,stepname):
        for step in self.steps:
            if step.name==stepname: return step 
        return None

    def load(self,readset):
        templated.load(self, vars=readset)

        # load steps.  (We're going to replace the current steps field, which holds a string of stepnames,
        # with a list of step objects
        stepnames=re.split('[,\s]+',self.steps)
        steps=[]                   # just to make sure
        for sn in stepnames:
            step=Step(name=sn)
            
            # load the step's template and self.update with the values:
            try:
                step.load()
            except IOError as ioe:
                die("Unable to load step %s" % sn, ioe)
            step.merge(readset)

            # add in items from step sections in <pipeline.syml>
            if self[step.name] == None:
                die("no section '%s' (sn=%s) in %s???" % (step.name, sn, self))

            try:
                # print "pipeline: self[%s] is\n%s" % (step.name, self[step.name])
                step.update(self[step.name])
                # print "pipeline: step %s is\n%s" %(step.name, step)
            except KeyError as e:
                die("no %s in\n%s" % (step.name, yaml.dump(self.__dict__)))
                
            # print "pipeline: step %s:\n%s" % (step.name, yaml.dump(step))
            
            steps.append(step)
            
        self.steps=steps

        return self
    
