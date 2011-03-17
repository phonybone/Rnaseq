#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import sys, yaml

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class ShellScript(Command):
    def run(self, **args):
        try:
            argv=args['argv']           # assume args=[path, author]
            options=Rnaseq.options
            readset_name=options.readset_name
            pipeline_name=options.pipeline_name

            readset=Readset(name=readset_name).load() 
            pipeline=Pipeline(name=pipeline_name, readset=readset)
            pipeline.load()
            pipeline.update(Rnaseq.config)

            close_file=False
            try:
                output_file=argv[2]     # [0] is program name, [1] is command
                f=open(output_file,"w")
                close_file=True
            except IndexError:
                f=sys.stdout

            script=pipeline.sh_script()
            f.write(script)
            if (close_file):
                f.close()
                print "%s written" % output_file

        except KeyError as e:
            die(MissingArgError(str(e)))
        except IndexError as e:
            die(UserError("Missing args in load"))

#print __file__, "checking in"
