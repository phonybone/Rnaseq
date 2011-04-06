from dict_like import dict_like

# This class overrides dict_like.__getitem__ such that if a key is not found, it returns
# a string "${%s}" % key.  That is, is returns the key prefixed with "${" and suffixed with "}"
# When used with evoque, it has the effect of leaving un-found items untouched, referenced by evoque as ${key},
# without throwning an error.


class evoque_dict(dict):
    def __init__(self,**args):
        dict.__init__(self,**args)
        for k,v in args.items():
            self[k]=v
            setattr(self,k,v)
        self.missing_keys=[]

        

    def __getitem__(self,key):
        try:
            v=dict.__getitem__(self,key)
            return v
        except KeyError as ie:
            try:
                return getattr(self,key)
            except AttributeError as ie:
                self.missing_keys.append(key)
                return "${%s}" % key

    def copy(self,*args):
        dict.copy(self.__dict__,*args)
        return self

        
