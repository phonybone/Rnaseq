#-*-python-*-
from dict_like import *
import yaml

class Pipeline(dict_like):
    attrs={'name':None,
           'steps':[],
           }

    # class vars
    template_dir='/proj/hoodlab/share/vcassen/rna-seq/rnaseq/templates' # fixme
    
    def __init__(self,args):
        self.name=args['name']
        self.steps=[]

    def template(self):
        template_file="%s/%s.syml" % (self.template_dir, self.name)
        f=open(template_file)
        tmpl=f.read()
        f.close()
        return tmpl
    
    def load(self):
        tmpl=self.template()
        self.update(yaml.load(tmpl))
        return self

