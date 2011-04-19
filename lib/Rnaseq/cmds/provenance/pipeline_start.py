#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import time

# usage: 


class PipelineStart(Command):
    def usage(self):
        return "usage: pipeline_start <pipelinerun_id>"

    def description(self):
        return "record provenance when one step finishes and the next begins"

    def run(self, *argv, **args):
        try:
            config=args['config']
            pipelinerun_id=int(argv[0][2])
            
        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()

        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        pipeline_run.status='started'
        pipeline_run.start_time=int(time.time())

        session.commit()
        print "pipeline '%s' started" % pipeline.name
