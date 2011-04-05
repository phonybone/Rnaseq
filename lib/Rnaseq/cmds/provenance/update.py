#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class Update(Command):
    def usage(self):
        return "usage: update <class> <id> <field> <value>"

    def description(self):
        return "update a database object"

    def run(self, *argv, **args):
        try:
            dbh=args['dbh']
            config=args['config']
            (classname,id,field,value)=argv[0][2:6]

        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()
        klass=globals()[classname]
        print "klass is %s" % klass
        for obj in session.query(klass):
            print "got %s %s (%s)" % (klass.__name__,obj)



#print __file__, "checking in"
