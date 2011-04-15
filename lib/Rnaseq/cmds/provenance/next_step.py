#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *

# usage: 


class NextStep(Command):
    def usage(self):
        return "usage: next_step <pipelinerun_id> <last_stepname> <retcode>"

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

        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        if pipeline_run==None:
            raise UserError("No pipeline run for pipelinerun_id=%s" % pipelinerun_id)
        pipeline=session.query(Pipeline).filter_by(id=pipeline_run.pipeline_id).first()
        if pipeline==None:
            raise UserError("No pipeline for pipeline_id=%s" % pipeline_run.pipeline_id)


        if retcode==0:                   # success!
            pass
        # Record successful status for last step
        # Update status of pipeline run object (last step completed ok)
        # Create new step_run object and insert it (unless this is the last step, excluding footer)
        # If last_step was the final step in the pipeline, record pipeline success
        
        # If last step failed:
        # Record failed status for last step
        # Record failed status for pipeline
        





        session.commit()



