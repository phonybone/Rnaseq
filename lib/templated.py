#-*-python-*-

# Mixin class that allows loading from a yaml (or superyaml?) file

import yaml,re
from dict_like import dict_like
from evoque import *
from evoque.domain import Domain
from evoque_dict import evoque_dict     # not part of official evoque lib; my own addition
from warn import *

class templated(dict_like):
    # class vars
    template_dir='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates' # fixme; get value from a config file
    attrs={'name':None,
           'type':None,
           'filename':None,             # alternate to template_filename
           }
    
    def template(self):
        template_file="%s/%s/%s.syml" % (self.template_dir, self.type, self.name)
        f=open(template_file)           # fixme: yaml_loadable
        tmpl=f.read()
        f.close()
        return tmpl
    

    def template_file(self):
        try:
            if self['filename'] != None:
                tf=self['filename']
                # print "template_file: tf is %s" % tf
                return tf
            else:
                assert self.name, "no name in\n %s" % self
                assert self.type, "no type in\n %s" % self
                return "%s/%s.syml" % (self.type, self.name)
        except KeyError as barf:
            print "KeyError %s: self is %s" % (barf, self)
            assert self.name, "no name in\n %s" % self
            assert self.type, "no type in\n %s" % self
            return "%s/%s.syml" % (self.type, self.name)
            


    # load a temlplate (either default or as passed), call yaml.load on the template, and store the resulting dict in
    # our own dict (without overwrites, as per dict.update())
    # fixme: this is a good place to examine inserting superyaml code; but so far, no need
    def load(self, **args):

        domain=Domain(self.template_dir)
        template=domain.get_template(self.template_file())
        vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
        yaml_str=template.evoque(evoque_dict().update(vars)) 

        # print "yaml_str:\n%s" % yaml_str
        d=yaml.load(yaml_str)           # fixme: what if template isn't yaml???
        try:
            self.update(d)
        except ProgrammerGoof as oopsie:
            if (oops.matches('not a dict or dict_like')): pass
            else: raise oopsie
            
        return self

        
    def eval_tmpl(self,**args):
        assert self.name
        assert self.type

        domain=Domain(self.template_dir)
        tf=self.template_file()
        print "templated: tf is %s" % tf
        template=domain.get_template(tf)
        vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
        output=template.evoque(evoque_dict().update(vars))
        return output



if __name__ == '__main__':
    import os
    path=os.path.normpath(os.path.abspath(__file__)+"../../../t/templated/test_all.py")
    execfile(path)
