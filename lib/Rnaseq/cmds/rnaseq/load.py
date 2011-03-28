#-*-python-*-
from warn import *
from Rnaseq import RnaseqGlobals
from Rnaseq.command import *
import yaml

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class Load(Command):
    def description(self):
        return "load a pipeline and quit (debugging tool)"

    def run(self, *argv, **args):
        try:
            options=argv['options']
            readset_name=options.readset_name
            pipeline_name=options.pipeline_name
            if readset_name==None or pipeline_name==None:
                raise UserError(RnaseqGlobals.usage)

            readset=Readset(name=readset_name).load() 
            pipeline=Pipeline(name=pipeline_name, readset=readset)
            pipeline.update(RnaseqGlobals.config)

        except KeyError as e:
            raise MissingArgError("missing arg: %s" % str(e))
        except IndexError as e:
            raise UserError("Missing args in load")



#print __file__, "checking in"
