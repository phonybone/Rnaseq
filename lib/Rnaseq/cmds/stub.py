#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class Stub(Command):
    def run(self, **args):
        try:
            argv=args['argv']
            dbh=args['dbh']
            options=args['options']
        except IndexError as ie:
            raise MissingArgError(str(ie))


    def description(self):
        return "print this help information"

#print __file__, "checking in"
