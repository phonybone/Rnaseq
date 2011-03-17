# -*-python-*-
# A class that expands on yaml config files
# Allows global variable substitution
# Allows self-referential partial values

import yaml, re, pdb, os, sys, logging
from evoque import *
from evoque.domain import Domain
from dict_like import dict_like
from warn import *
from evoque_dict import evoque_dict

class superyaml(dict_like):
    attrs={'domain':None,
           'visited':{},
           }
    _re_get_exact=re.compile('\$\(([^)]*?)\)$')
    _re_get_many=re.compile('\$\((.*?)\)')

    def __init__(self,**args):
        self.attrs.update(args)
        dict_like.__init__(self,**args)

########################################################################

    # return a dict derived from the template and vars:
    def load(self,template,vars):
        dp=os.path.dirname(template)
        if dp != '':
            self.domain=dp
            
        filename=os.path.basename(template)

        try:
            d=Domain(self.domain, quoting=None) # fixme: what do we really want for quoting?
            t=Domain(self.domain).get_template(filename, quoting="str")
        except Exception as e:
            print "(domain is %s)" % self.domain
            raise e

        evars=evoque_dict()             # special dict that returns missing keys as "${key}"
        evars.update(vars)
        yaml_txt=t.evoque(evars)

        # fix eval errors:
        # fixed_yaml=re.sub('\[EvalError\(([a-z_]+)\)]', "${\g<1>}", yaml_txt) # ooh, magic! great.
        # fixed_yaml=re.sub('\[NameError: name &#39; ([a-z_]+)\)]', "${\g<1>}", yaml_txt) # ooh, magic! great.
        # fixed_yaml=re.sub('&lt;built-in function ([a-z_]+)&gt;', "${\g<1>}", fixed_yaml) # christ, more magic

#        warn("syml.load: fixed_yaml is %s" % fixed_yaml)
        d=yaml.load(yaml_txt)
            
        # "fix" config; ie, resolve referenced values
        d=self._fix_hash(d,d)
        return d
        

########################################################################

    def _get_val(match):
        k=match.group(1)
        v=None
        exp="conf%s" % k
        # warn("1. exp is %s" % exp)
        try: v=eval(exp)
        except: pass
        return v
    
########################################################################
# have to handle three separate cases:
# 1: val doesn't contain a get() clause at at all; return val as is
# 2: val exactly matches one get() clause: do the lookup, value can be anything
# 3: val embeds one or more get() clauses; do the lookups, but all values must be strings
    def _fix_value(self, val, conf):
        if val in self.visited:
            if self.visited[val]==None:
                raise Exception("%s: part of cycle" % val)
            else:
#                print "(cached): returning %s" % self.visited[val]
                return self.visited[val]
        else:
            self.visited[val]=None
            
        m=superyaml._re_get_exact.match(val) # defined near top of class
        if m:                               # exact match; replace with anything
            exp=m.group(1)

            try:
                # warn("\n\n\n2. exp is %s\n\n\n" % exp)
                new_val=eval("conf%s" % exp)  # look up exp in conf
            except Exception as e:
                print "eval error: \"conf%s\n(in \"%s\")\"" % (m.groups()[0], exp)
                print "%s: %s" %(type(e),e)
                from pprint import pprint
                pprint(conf)
                raise e
#                sys.exit(1)
                
            if superyaml._re_get_many.match(new_val): # do we need to continue?
                new_val=self._fix_value(new_val,conf) # recur

            # need to store new_val in visited?
            self.visited[val]=new_val
#            print "self._fix_value (1) returning %s" % new_val
            return new_val

        # look for multiple matches
        new_val=''
        i=0
        for m in superyaml._re_get_many.finditer(val):
            new_val+=val[i:m.start()]   # append next unmatched portion of original
            try:
                exp="conf%s" % m.groups()[0]
                # warn("3. exp is %s" % exp)
                new_val+=str(eval(exp)) # append lookup of match
            except Exception as e:
                print "eval error: \"conf%s (in \"%s\")\"" % (m.groups()[0], val)
                print "%s: %s" %(type(e),e)
                from pprint import pprint
                pprint(conf)
                raise e
#                sys.exit(1)

            i=m.end()                   # advance i past match
        new_val+=val[i:]                # append last part of original val

        # do we need to recur?
        if superyaml._re_get_many.match(new_val):
            new_val=self._fix_value(new_val,conf)

#        print "self._fix_value (2) returning %s" % new_val

        self.visited[val]=new_val
        return new_val




########################################################################
    def _fix_hash(self,h,conf):
        new_h={}
        top_level=h==conf
        for k,v in h.items():
            k=self._fix_value(k,conf)
                
            if type(v)==type([]):   # list
                new_h[k]=self._fix_list(v,conf)
            elif type(v)==type({}):   # another hash
                new_h[k]=self._fix_hash(v,conf)
            elif type(v)==type(''):   # string
                new_h[k]=self._fix_value(v,conf)
                if top_level: conf[k]=new_h[k]
            else: new_h[k]=v                  # something else; int, float, ...?
            
        return new_h
            
            
########################################################################
    def _fix_list(self, l,conf):
        new_l=[]
        for e in l:
            if type(e)==type([]):   # list
                new_l.append(self._fix_list(e,conf))
            elif type(e)==type({}):   # another hash
                new_l.append(self._fix_hash(e,conf))
            elif type(e)==type(''):   # string
                new_l.append(self._fix_value(e,conf))
            else: new_l.append(e)
            
        return new_l

########################################################################


print __file__,"checking in"
        
#if __name__ == '__main__':
#    import doctest
#    doctest.testfile('test1.txt')
