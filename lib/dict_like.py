import yaml
from warn import *

class dict_like:
    attrs={}                            # sub classes override this

    def __init__(self,**arghash):
        # first set args named in attrs; this allows unnamed attrs to have default values as defined in attrs
        for attr,v in self.attrs.items():
            if arghash.has_key(attr):
                self[attr]=arghash[attr]
            else: 
                self[attr]=self.attrs[attr]
        # print "dict_like:__init__: args are %s" % yaml.dump(arghash)
        # print "dict_like:__init__: self is %s (%s)" % (yaml.dump(self), type(self))


    def __getitem__(self,attr):
        return self.__dict__[attr]

    def __setitem__(self,attr,val):
        self.__dict__[attr]=val
        return val
    
    def attrs_dict(self):
        return self.__dict__
    
    # add a new attribute to an object:
    def add_attr(self,*args):
        attr=args[0]                    # let this fail if not present
        try:
            val=args[1]
        except IndexError as e:
            val=None                    # ok to fail
        self.__dict__[attr]=val
        return self

    # WARNING! This lets you get around the restriction that the object can contain only keys found in attrs!
    def update(self,d):
        if (not isinstance(d,dict)):
            if (isinstance(d,dict_like)): # dict_like instances are not instances of dict
                d=d.attrs_dict()        # get the dict part of a dict_like object
            else:
                raise ProgrammerGoof("%s: not a dict or dict_like" % d)

        self.__dict__.update(d)
        return self
    
    # like update, but doesn't clobber existing keys
    def merge(self,d):
        if (not isinstance(d,dict)):    # fixme: dry error
            if (isinstance(d,dict_like)):
                d=d.attrs_dict()
            else:
                raise ProgrammerGoof("%s: not a dict or dict_like" % d)

        for (k,v) in d.items():
            if (k not in self.__dict__): self[k]=v

        return self

    def __str__(self):
        s="%s:\n" % self.__class__
        for k,v in self.__dict__.items():
            if isinstance(k, str):
                s+="%s: %s\n" % (k,v)
            else:
                s += "%s: c=%s:%s" % (k,v.__class_,yaml.dump(v))
        return s


