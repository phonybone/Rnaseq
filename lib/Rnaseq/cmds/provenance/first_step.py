#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import time

# usage: 


class MidStep(Command):
    def usage(self):
        return "usage: mid_step <pipelinerun_id> <last_stepname> <retcode>"

    def description(self):
        return "record provenance when one step finishes and the next begins"

    def run(self, *argv, **args):
        try:
            config=args['config']
            (pipelinerun_id, last_stepname, retcode)=argv[0][2:5]
            pipelinerun_id=int(pipelinerun_id)
            retcode=int(retcode)
            
        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()
