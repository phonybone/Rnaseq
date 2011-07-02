import yaml
from Rnaseq import *
from RnaseqGlobals import *

class StepFactory(object):
    def __init__(self, pipeline):
        self.pipeline=pipeline

    
    def new_step(self, stepname, **kwargs):
        try:
            mod=__import__('Rnaseq.steps.%s' % stepname)
        except ImportError as ie:
            raise ConfigError("error loading step '%s': %s" % (stepname, str(ie)))
        
        mod=getattr(mod,"steps")

        try:
            mod=getattr(mod,stepname)
            kls=getattr(mod,stepname)            
        except AttributeError as ae:
            raise ConfigError("step %s not defined: "+str(ae))

        # add items to kwargs:
        pipeline=self.pipeline
        kwargs['pipeline']=pipeline
#        kwargs['readset']=pipeline.readset
        step=kls(**kwargs)
        
        # If the step defines an attribute named export (fixme: and it's a list),
        # copy the step's exorted attributes to the pipeline:
        if hasattr(step,'export'):
            try:
                for attr in step.export:
                    attr_val=getattr(step,attr)
                    setattr(pipeline,attr,attr_val) # fixme: setting pipeline attribute from different class ok?
                    pipeline.step_exports[attr]=attr_val # fixme: setting pipeline attribute from different class ok?
            except AttributeError as ae:
                raise ConfigError("step %s tries to export missing attr '%s'" % (step.name, attr))
        
        return step

        
