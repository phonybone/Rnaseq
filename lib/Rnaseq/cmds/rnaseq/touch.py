#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 

class Touch(Command):
    def run(self, *argv, **args):
        try:
            dbh=args['dbh']
            options=args['options']
        except KeyError as ke:
            raise MissingArgError(ke)
    
        try:
            path=argv[2]                # argv[0] is program, argv[1] is command
            with file(path, 'a'):
                os.utime(path, None)
        except IndexError as ie:
            ue=UserError(self.usage())
            raise ue

    def usage(self):
        return "usage: touch <path>"

    def description(self):
        return "print this help information"

#print __file__, "checking in"
