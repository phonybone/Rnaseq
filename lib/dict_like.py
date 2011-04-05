import yaml
from warn import *

class dict_like(object):
    attrs={}                            # sub classes override this

    def __init__(self,**args):
        print "%s: args are %s" % (type(self), args)
        for k,v in args.items():
            setattr(self,k,v)
        print "done now: self is %s" % self
    
    def __str__(self):
        s="%s:\n" % self.__class__
        for k,v in self.__dict__.items():
            if isinstance(k, str):
                s+="%s: %s\n" % (k,v)
            else:
                s += "%s: c=%s:%s" % (k,v.__class_,yaml.dump(v))
        return s

########################################################################
    
    # WARNING! This lets you get around the restriction that the object can contain only keys found in attrs!
    def update1(self,d):
        if (not isinstance(d,dict)):
            if (isinstance(d,dict_like)): # dict_like instances are not instances of dict
                d=d.attributes()        # get the dict part of a dict_like object
            else:
                raise ProgrammerGoof("%s: not a dict or dict_like" % d)

        self.__dict__.update(d)
        return self
    
    # like update, but doesn't clobber existing keys
    def merge1(self,d):
        if (not isinstance(d,dict)):    # fixme: dry error
            if (isinstance(d,dict_like)):
                d=d.attributes()
            else:
                raise ProgrammerGoof("%s: not a dict or dict_like" % d)

        for (k,v) in d.items():
            if (k not in self.__dict__): self[k]=v

        return self


