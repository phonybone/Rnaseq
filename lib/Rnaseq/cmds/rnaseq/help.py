#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import yaml, os

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class Help(Command):
    def run(self, *argv, **args):
        cmds=Rnaseq.config['cmds'].keys()
        cmds.sort()
        prog_name=os.path.basename(argv[0])
        cf=CmdFactory(program=prog_name)
        print "%s commands:\n" % prog_name
        for cmd_name in cmds:
            cmd=cf.new_cmd(cmd_name)
            print "%s:\t%s" % (cmd_name, cmd.description())
        print

    def description(self):
        return "print this help information"

    def usage(self):
        return "help"

#print __file__, "checking in"
