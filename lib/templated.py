#-*-python-*-

# Mixin class that allows loading from a yaml (or superyaml?) file

import yaml
import re

class templated:
    # class vars
    template_dir='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates' # fixme; get value from a config file

    def template(self):
        template_file="%s/%s.syml" % (self.template_dir, self.name)
        f=open(template_file)
        tmpl=f.read()
        f.close()
        return tmpl
    
    # load a temlplate (either default or as passed), call yaml.load on the template, and store the resulting dict in
    # our own dict (without overwrites, as per dict.update())
    def load(self):
        tmpl=self.template()
        self.update(yaml.load(tmpl))    # calling update here is more evidence that dict_like and templated should be the same class
        return self

    
