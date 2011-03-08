from warn import *
from string_helpers import dash2camel_case
import re


class ProvCmdFactory:
    cmds={}

    # add a command, using its name and the file (relative to lib/Rnaseq/prov):
    def add_cmd(self,cmd_name,cmd_file):
        self.cmds[cmd_name]=cmd_file

    # return an instance of ProvCmd class according to cmd type
    def new_cmd(self,cmd_type):
        if cmd_type not in self.cmds:
            die(UserError("Unknown command '%s'" % cmd_type))

        cmd_file=self.cmds[cmd_type]
        cmd_file=re.sub('.py','',cmd_file)
        cmd_dotpath="Rnaseq.prov.%s" % cmd_file

        mod=__import__(cmd_dotpath)
        for comp in cmd_dotpath.split(".")[1:]:
            mod=getattr(mod,comp)

        klass=getattr(mod,dash2camel_case(cmd_file))
        return klass()
        

