from evoque import *
from evoque.domain import Domain
import os, yaml

def evoque_template(template, vars, *more_vars, **kw_vars):
    domain=Domain(os.getcwd(), errors=4) # we actually don't care about the first arg
    domain.set_template('template', src=template)
    tmp=domain.get_template('template')
    cvars=vars.copy()
    
    for v in more_vars:
        try: cvars.update(v)
        except Exception as e:
            print "caught %s" % e

    for k,v in kw_vars.items():
        cvars[k]=kw_vars[k]
        
    return tmp.evoque(cvars)
