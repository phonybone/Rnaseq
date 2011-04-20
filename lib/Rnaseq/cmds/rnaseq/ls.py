from Rnaseq import *
from Rnaseq.command import *
from RnaseqGlobals import *

class Ls(Command):

    def description(self):
        return "display information about pipelines"

    def usage(self):
        return "ls -p <pipeline> []"

    def run(self, *argv, **args):
        try:
            config=args['config']
            pipeline_name=config['pipeline_name']
        except KeyError as e:
            raise MissingArgError(str(e))
            
        try: argv=argv[0]
        except IndexError as e: raise ProgrammerGoof(e)

        pipeline=Pipeline(name=pipeline_name, readset={}).load()
        print "yay"



        session=RnaseqGlobals.get_session()



