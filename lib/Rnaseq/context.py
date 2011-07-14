from Rnaseq import *
from RnaseqGlobals import *

class Context(object):
    def __init__(self, readset):
        self.readset=readset
        self.inputs={}
        self.outputs={}

    def load_io(self,pipeline):
        for step in pipeline.steps:
            try: self.outputs[step.name]=step.outputs()
            except AttributeError: self.outputs[step.name]=[]
            
            self.inputs[step.name]=pipeline.convert_inputs(step.name, self)
        return self

print __file__,"checking in"
