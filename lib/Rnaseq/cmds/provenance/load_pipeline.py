#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import yaml

# usage: 


class LoadPipeline(Command):
    def usage(self):
        return "usage: load_pipeline <pipeline>"

    def description(self):
        return "load a pipeline into the database"

    def run(self, *argv, **args):
        try:
            config=args['config']
            pipeline_name=argv[0][2]

        except ValueError as ie:
            #print "caught %s" % ie
            raise UserError(self.usage())

        pipeline=Pipeline(name=pipeline_name, path=os.path.join(RnaseqGlobals.root_dir(),'templates','pipeline',pipeline_name+'.syml'))
        pipeline.store_db()
