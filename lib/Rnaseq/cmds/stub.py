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


    def run(self, *argv, **args):
        try:
            (arg1,arg2)=argv[0][2:3]
            config=args['config']
        except KeyError as ke:
            raise MissingArgError(str(ke))
        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()

        raise ProgrammerGoof("%s doesn't override run()" % self.__class__.__name__)


#print __file__, "checking in"
