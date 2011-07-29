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
            first_steprun_id=int(argv[0][3])

        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()
        now=int(time.time())
        
        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        if pipeline_run==None:
            die("No pipeline run object w/id=%d" % pipelinerun_id)
        pipeline_run.status='started'
        pipeline_run.start_time=now
        pipeline_run.current_step_run_id=first_steprun_id

        step_run=session.query(StepRun).filter_by(id=first_steprun_id).first()
        step_run.start_time=now
        step_run.status='started'

        session.commit()
        pipeline=session.query(Pipeline).filter_by(id=pipeline_run.pipeline_id).first()

