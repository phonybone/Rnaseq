#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class Load(Command):
    def description(self):
        return "load a pipeline and quit (debugging tool)"

    def usage(self):
        return "usage: load -p <pipeline> -r <readset>"

    def run(self, *argv, **args):
        try:
            config=args['config']
            readset_file=config['readset_file']
            pipeline_name=config['pipeline_name']
        except KeyError as e:
            raise MissingArgError(str(e))

        # have to create session before creating any objects that session adds, etc:

        readset=Readset(name=readset_file).load() 
        pipeline=Pipeline(name=pipeline_name, readset=readset)
        pipeline.update(RnaseqGlobals.config)
        pipeline.description='desc for juan'

        session=RnaseqGlobals.get_session() 
        session.add(pipeline)
        session.commit()



#print __file__, "checking in"
