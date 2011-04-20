#-*-python-*-
from warn import *
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from Rnaseq.command import *


class Insert(Command):
    def usage(self):
        return "usage: insert <class> [field='value']*"

    def description(self):
        return "insert a database object"
    
    def run(self, *argv, **args):
        try: classname=argv[0][2]                # [0] is script name, [1] is command
        except IndexError: raise UserError(self.usage())
        
        try: klass=globals()[classname]
        except KeyError: raise UserError("%s: unknown class" % classname)

        session=RnaseqGlobals.get_session()

        obj_hash={}
        paired=[p for p in argv[0] if re.match("\w+=\w+", p)]

        o=klass()
        for pair in paired:
            k,v=re.split("=",pair)
            o[k]=v
            setattr(o,k,v)
        print "o is %s" % o
        
        session.add(o)
        session.commit()
        print "%s inserted" % klass.__name__
