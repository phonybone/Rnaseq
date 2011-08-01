import yaml
from warn import *

class UserConfig(dict):
    def __init__(self,*args,**kwargs):
        from_dict=False
        try:
            d=args[0]                   # this is called where?
            self.update(d)
            from_dict=True
        except IndexError: pass

        for k,v in kwargs.items():
            self[k]=v

    def read(self,filename):
        try: f=open(filename)
        except IOError as ioe: raise UserError(ioe)
        except TypeError: return self
        
        try:
            user_config=yaml.load(f)
            self.update(user_config)
        except yaml.scanner.ScannerError as barf:
            raise ConfigError(barf)
        
        setattr(self,'filename',filename)
        return self

    # merge args in user_config into a pipeline
    # parses specific structure of dict:
    # args must be one entry from self['pipeline_runs'] and have a specific structure:
    # args['pipeline'] must be a string matching pipeline.name
    # any k,v entries in args where v is a scalar get merged into pipeline as an attribute,
    # unless pipeline.k is callable, in which case pipeline.k(v) is called to set the attribute (or whatever)
    # if k is a step name and v is a dict, then the step is update()'d with v
    def merge_args(self,pipeline,args):
        if 'pipeline' not in args: return self
        if args['pipeline']!=pipeline.name:
            raise UserError("pipeline name mismatch in %s: attempt to match user_config for '%s' with pipeline '%s'" % (self.filename, args['pipeline'], pipeline.name))
        for k,v in args.items():
            step=pipeline.step_with_name(k)
            if step != None:
                if type(v) != type({}):
                    raise ConfigError("%s: not a dict" % v)
                step.update(v)
            elif hasattr(pipeline,k) and callable(getattr(pipeline,k)):
                m=getattr(pipeline,k)
                try: m(v)                    
                except TypeError as te: raise ConfigError(te)
                    
            else:
                setattr(pipeline,k,v)
        return self

    def user_runs(self):
        try: return self['pipeline_runs']
        except: return [{}]
    
