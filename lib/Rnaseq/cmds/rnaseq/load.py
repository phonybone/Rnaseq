#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import yaml

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class Load(Command):
    def run(self, **args):
        try:
            argv=args['argv']           # assume args=[path, author]
            options=args['options']
            readset_name=options.readset_name
            pipeline_name=options.pipeline_name
            if readset_name==None or pipeline_name==None:
                raise UserError(Rnaseq.usage)

            readset=Readset(name=readset_name).load() 
            pipeline=Pipeline(name=pipeline_name)
            pipeline.load(readset)
            pipeline.update(options.config)

            print "pipeline.working_dir() is %s" % pipeline.working_dir()

        except KeyError as e:
            die(MissingArgError(str(e)))
        except IndexError as e:
            die(UserError("Missing args in load"))

#print __file__, "checking in"
