#-*-python-*-

# Mixin class that allows loading from a yaml (or superyaml?) file.
# yaml file must be located under the templated.template_dir subdir.
# templates are also processed through evoque, so they can contain ${substitutions}.  see load().
# It's getting messy the template does not contain yaml.

import yaml, re, os
from dict_like import dict_like
from evoque import *
from evoque.domain import Domain
from evoque_dict import evoque_dict     # not part of official evoque lib; my own addition
from warn import *

class templated(dict_like):
    # class vars
    template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../templates")


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
                return tf
            else:
                assert self.name, "no name in\n %s" % self
                assert self.type, "no type in\n %s" % self
                return "%s/%s.syml" % (self.type, self.name) # fixme: self.name is always the name of the template file?
        except KeyError as barf:
            # print "templated.template_file(): couldn't find key 'filename', so looking in default location"
            assert self.name, "no name in\n %s" % self
            assert self.type, "no type in\n %s" % self
            assert type(self.name)==type("string")
            assert type(self.type)==type("string")
            return "%s/%s.syml" % (self.type, self.name)
            


    # load a temlplate (either default or as passed), call yaml.load on the template, and store the resulting dict in
    # our own dict (without overwrites, as per dict.update())
    # fixme: this is a good place to examine inserting superyaml code; but so far, no need
    # returns self
    def load(self, **args):

        # get the template and call evoque() on it.  This should yield a yaml string
        try: 
            domain=Domain(self.template_dir, errors=4) # errors=4 means raise errors as an exception
            template=domain.get_template(self.template_file())
            vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
            #print "about to evoque: vars are:\n%s" % yaml.dump(vars)
            ev=evoque_dict().update(vars)
            try: 
                yaml_str=template.evoque(ev)
            except TypeError as te:
                print "te is %s (%s)" % (te, type(te))
                raise te

            # why we want to keep this: evoque_dicts protect us against simple Key errors, but not
            # errors of the type ${readset['missing_key']}
            except KeyError as ke:
                #print "ke is %s (%s)" % (ke, type(ke))
                raise ConfigError(str(ke))
            
        except ValueError as ve:
            mgroup=re.match('File \[(.*)\] not found', str(ve))
            import traceback
            traceback.print_exc()
            if mgroup:
                raise UserError("template error: %s %s not found" % (self.type, mgroup.group(1)))
            else:
                raise ve
        
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
        assert self.name
        assert self.type

        domain=Domain(self.template_dir)
        tf=self.template_file()
        #print "templated: tf is %s" % tf
        template=domain.get_template(tf)
        vars=args['vars'] if args.has_key('vars') else {} # consider default of self instead of {}?  Or is that stupid?
        output=template.evoque(evoque_dict().update(vars))
        return output



if __name__ == '__main__':
    import os
    path=os.path.normpath(os.path.abspath(__file__)+"../../../t/templated/test_all.py")
    execfile(path)
