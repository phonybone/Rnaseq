from Rnaseq.prov.create_table import *
from Rnaseq.prov.insert_prov import *
from warn import *

class ProvCmdFactory:
    cmds={}

    def new_cmd(self,cmd_type):
        if cmd_type not in self.cmds:
            die(ProgrammerGoof("Unknown command '%s'" % cmd_type))
        cmd_classname=self.cmds[cmd_type]
        cmd_class=globals()[cmd_classname]
        return cmd_class()
    
    def add_cmd(self,cmd_name,cmd_class):
        self.cmds[cmd_name]=cmd_class

        
