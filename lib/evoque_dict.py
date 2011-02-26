from dict_like import dict_like

class evoque_dict(dict_like):
    def __getitem__(self,key):
        try:
            v=self.__dict__[key]
            return v
        except KeyError as ie:
            return "${%s}" % key

    def copy(self,*args):
        dict.copy(self.__dict__,*args)
        return self

        
