#-*-python-*-
from warn import *
from Rnaseq import *
from RnaseqGlobals import *
from Rnaseq.command import *

class ListFiles(Command):
    def usage(self):
        return "usage: ls <class> [field=val]+"
    
    def description(self):
        return "select and list the contents of a table"

    def run(self, *argv, **args):
        try:
            config=args['config']
            classname=argv[0][2]

        except IndexError as ie:
            raise UserError(self.usage())
        except KeyError as ie:
            raise UserError(self.usage())

        try: klass=globals()[classname]
        except KeyError as ke: raise UserError("%s: unknown class" % str(ke))
            
        session=RnaseqGlobals.get_session()
        q=session.query(klass)

        for pair in argv[0][3:]:
            print "pair is %s" % pair
            try:
                (field,val)=re.split("=",pair)
                print "field is %s, val is %s" % (field,val)
                q=q.filter("%s=%s" % (field,val))
            except Exception as e:
                print "caught %s" % e
        
        for r in q:
            print "r is %s" % r


#print __file__, "checking in"
