#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class Stub(Command):
    def usage(self):
        return "usage: update -p <pipeline_name> --status <status>"

    def description(self):
        return "update the status of a pipeline"

    def run(self, *argv, **args):
        try:
            dbh=args['dbh']
            options=args['options']
            pipeline_name=
        except IndexError as ie:
            raise MissingArgError(str(ie))

        pipeline=Pipeline.fetch

    def description(self):
        return "print this help information"

#print __file__, "checking in"
