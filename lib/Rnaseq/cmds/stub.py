#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class Stub(Command):
    def usage(self):
        raise ProgrammerGoof("%s doesn't override usage()" % self.__class__.__name__)

    def description(self):
        raise ProgrammerGoof("%s doesn't override description()" % self.__class__.__name__)


    def run(self, **args):
        try:
            dbh=args['dbh']
            options=args['options']
        except IndexError as ie:
            raise MissingArgError(str(ie))

        raise ProgrammerGoof("%s doesn't override run()" % self.__class__.__name__)


#print __file__, "checking in"
