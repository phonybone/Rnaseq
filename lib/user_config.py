import yaml
from warn import *

class UserConfig(dict):
    def __init__(self,*args,**kwargs):
        from_dict=False
        try:
            d=args[0]
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
        
        return self

    def merge_args(self,pipeline,args):
        assert(args['pipeline']==pipeline.name)
        for k,v in args.items():
            step=pipeline.stepWithName(k)
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
        try:
            return self['pipeline_runs']
