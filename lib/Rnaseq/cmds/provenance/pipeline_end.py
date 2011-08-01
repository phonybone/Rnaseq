#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import time

# usage: 


class PipelineEnd(Command):
    def usage(self):
        return "usage: provenance pipeline_end <pipelinerun_id> <last_step_run_id>"

    def description(self):
        return "set the final status for a pipeline run"

    def run(self, *argv, **args):
        try:
            config=args['config']
            pipelinerun_id=int(argv[0][2])
            
        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()
        now=int(time.time())
        
        # record pipeline finish:
        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        pipeline_run.finish_time=now
        pipeline_run.status='finished'
        pipeline_run.successful=True    # we can assume this because if any of the steps failed, we don't even call this command

        session.commit()
