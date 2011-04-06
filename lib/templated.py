#-*-python-*-

# Mixin class that allows loading from a yaml (or superyaml?) file.
# yaml file must be located under the templated.template_dir subdir.
# templates are also processed through evoque, so they can contain ${substitutions}.  see load().
# It's getting messy the template does not contain yaml.

from RnaseqGlobals import RnaseqGlobals
import yaml, re, os
import path_helpers
from dict_like import dict_like
from evoque import *
from evoque.domain import Domain
from evoque_dict import evoque_dict     # not part of official evoque lib; my own addition
from warn import *


class templated(dict):
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)
        self.dict=self.__dict__         # convenience, hope it doesn't bite us

    def __str__(self):
        try:
            return yaml.dump(self)
        except:
            return object.__str__(self)

    def merge(self,d):                  # fixme: should go into dict_helper class or some such
        if (not isinstance(d,dict)):    
            if (isinstance(d,templated)):
                d=d.dict
            else:
                raise ProgrammerGoof("%s: not a dict or templated" % type(d))

        for (k,v) in d.items():
            if (k not in self.dict):
                self[k]=v

        return self

        

    ########################################################################

    # class vars
    template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../templates")
    #template_dir=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'),"templates") # RnaseqGlobals not init'd yet

    def template(self):
        template_file="%s/%s/%s.syml" % (self.template_dir, self.type, self.name)
        f=open(template_file)           # fixme: yaml_loadable
        tmpl=f.read()
        f.close()
        return tmpl
    

    def template_file(self):
        try:
            return path_helpers.sanitize(self.filename)
        except AttributeError:
            return path_helpers.sanitize("%s/%s.%s" % (self.type, self.name, self.suffix)) # fixme: self.name is always the name of the template file?
            

    # load a temlplate (either default or as passed), call yaml.load on the template, and store the resulting dict in
    # our own dict (without overwrites, as per dict.update())
    # fixme: this is a good place to examine inserting superyaml code; but so far, no need
    # returns self
    def load(self, **args):
        assert hasattr(self,'name')     # can't do "assert self.name" because that throws Attribute error
        assert hasattr(self,'type')     # before assert even gets to it

        # get the template and call evoque() on it.  This should yield a yaml string
        try:
            domain=Domain(self.template_dir, errors=4, quoting=str) # errors=4 means raise errors as an exception
        except ValueError as ve:
            raise ConfigError("Error in setting template directory: "+str(ve))
        
        try: 
            tf=self.template_file()
            template=domain.get_template(tf)
        except ValueError as ve:
            raise UserError("%s '%s': missing template file %s/%s" % (self.type, self.name, self.template_dir, self.template_file()))
        
        vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
        #print "%s.%s: about to evoque: vars are:\n%s" % (self.name, self.type, yaml.dump(vars))
        ev=evoque_dict()
        if 'vars' in args and args['vars']==None:
            raise ProgrammerGoof("vars is None")
        ev.update(vars)
        #print "templated: ev is %s\nvars is %s" % (ev,vars)
        try: 
            yaml_str=template.evoque(ev)
            # why we want to keep this: evoque_dicts protect us against simple Key errors, but not
            # errors of the type ${readset['missing_key']}
        except KeyError as ke:
            #print "ke is %s (%s)" % (ke, type(ke))
            raise ConfigError("%s '%s': %s" % (self.type, self.name, ke))
        except AttributeError as ae:
            raise ConfigError("%s '%s': %s" % (self.type, self.name, ae))
        except TypeError as ae:
            raise ProgrammerGoof("%s '%s': %s" % (self.type, self.name, ae))
        
        # Check if all keys are needed:
        if 'final' in args and args['final']: # might be present but false; perl rules!
            if len(ev.missing_keys)>0:
                raise ConfigError("%s %s: missing keys in final load: %s" %(self.type, self.name, ", ".join(str(i) for i in (set(ev.missing_keys)))))


        # call yaml.load on the string produced above, then call self.update() on the resulting dict object
        #print "yaml_str:\n%s" % yaml_str
        d=yaml.load(yaml_str)           # fixme: what if template isn't yaml???
        try:
            self.update(d)
        except ProgrammerGoof as oopsie:
            if (re.search('not a dict or dict_like', str(oopsie))): pass
            else: raise oopsie
            
        return self

    # 
    def eval_tmpl(self,**args):
        assert hasattr(self,'name')     # can't do "assert self.name" because that throws Attribute error
        assert hasattr(self,'type')     # before assert even gets to it

        domain=Domain(self.template_dir, errors=4)
        tf=self.template_file()
        #print "templated: tf is %s" % tf
        template=domain.get_template(tf)
        vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
        try:
            ev=evoque_dict().update(vars)
            output=template.evoque(ev)
        except (KeyError, AttributeError, TypeError) as any_e:
            raise ConfigError("%s '%s': %s" % (self.type, self.name, any_e))

        # Check if all keys are needed:
        if 'final' in args and args['final']:
            if len(ev.missing_keys)>0:
                raise ConfigError("%s %s: missing keys in final load: %s" %(self.type, self.name, ", ".join(ev.missing_keys)))


        return output



if __name__ == '__main__':
    import os
    path=os.path.normpath(os.path.abspath(__file__)+"../../../t/templated/test_all.py")
    execfile(path)
