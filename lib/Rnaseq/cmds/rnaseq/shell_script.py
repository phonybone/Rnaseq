#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import sys, yaml

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class ShellScript(Command):
    def usage(self):
        return "usage: sh [output_file] -p <pipeline> -r <readset> [options]"

    def description(self):
        return "generate a shell script determining the pipeline's excecution"
    
    def run(self, *argv, **args):
        try:
            config=args['config']
        except KeyError as e:
            raise MissingArgError(str(e))
            
        try:
            argv=argv[0]
        except IndexError as e:
            raise ProgrammerGoof(e)

        try:
            readset_name=config['readset_name']
            pipeline_name=config['pipeline_name']
        except IndexError:
            raise UserError(self.usage())

        readset=Readset(name=readset_name).load() 
        pipeline=Pipeline(name=pipeline_name, readset=readset)
        pipeline.load()
        pipeline.update(RnaseqGlobals.config)


        try:
            output_file=argv[2]     # [0] is program name, [1] is command
            output_path=os.path.join(pipeline.working_dir(), output_file)
        except IndexError:
            output_path=os.path.join(pipeline.working_dir(), pipeline.scriptname())

        f=open(output_path, "w")
        script=pipeline.sh_script()
        f.write(script)
        f.close()
        print "%s written" % output_path


#print __file__, "checking in"
