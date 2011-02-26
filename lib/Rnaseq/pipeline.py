#-*-python-*-

import yaml
import re

from warn import warn,die
from dict_like import *
from templated import *
from step import *

class Pipeline(dict_like, templated):
    attrs={'name':None,
           'steps':[],
           }

    def __init__(self,args):
        self.name=args['name']
        self.steps=[]

    def load(self):
        templated.load(self)

        # load steps.  (We're going to replace the current steps field, which holds a string of stepnames,
        # with a list of step objects
        stepnames=re.split('[,\s]+',self.steps)
        steps=[]                   # just to make sure
        for sn in stepnames:
            step=Step('name': sn)

            try: step.load()
            except IOError as ioe: die("Unable to load step %s" % sn, ioe)
            
            steps.append(step)
            
        self.steps=steps

        return self
    
