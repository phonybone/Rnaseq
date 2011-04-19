from Rnaseq import *
from Rnaseq.command import *

class Ls(Command):
    def run(self, *argv, **args):
        try:
            config=args['config']
            readset_file=config['readset_file']
            pipeline_name=config['pipeline_name']
        except KeyError as e:
            raise MissingArgError(str(e))
            
        try:
            argv=argv[0]
        except IndexError as e:
            raise ProgrammerGoof(e)



    def description(self):
        return "display information about pipelines"

    def usage(self):
        return "help"

