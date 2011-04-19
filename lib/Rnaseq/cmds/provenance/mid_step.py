#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import time

# usage: 


class MidStep(Command):
    def usage(self):
        return "usage: mid_step <pipelinerun_id> <steprun_id> <next_steprun_id> <retcode>"

    def description(self):
        return "record provenance when one step finishes and the next begins"

    def run(self, *argv, **args):
        try:
            config=args['config']
            (pipelinerun_id, steprun_id, next_steprun_id, retcode)=argv[0][2:5]
            pipelinerun_id=int(pipelinerun_id)
            retcode=int(retcode)
            
        except ValueError as ie:
            raise UserError(self.usage())

        session=RnaseqGlobals.get_session()

        # get pipeline_run object:
        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        if pipeline_run==None:
            raise UserError("No pipeline run for pipelinerun_id=%s" % pipelinerun_id)

        # get the step_run object, then the step
        step_run=session.query(StepRun).filter_by(id=steprun_id).first()
        if not step_run:
            print "steprun_id=%s: no last step_run???" % steprun_id
            return

        step=session.query(Step).filter_by(id=step_run.step_id).first()
        
        now=int(time.time())
        if retcode==0:                   # last step was a success!
            # set last step status:
            step_run.successful=True
            step_run.finish_time=now
            step_run.status='finished' # or something...

            # set pipeline_run status:
            pipeline_run.status="%s finished" % step.name

            # set the start time for the next step_run:
            next_steprun=session.query(StepRun).filter_by(id=next_steprun_id).first()
            next_steprun.start_time=now

        else:                           # last step failed (boo)
            step_run.successful=False
            step_run.finish_time=now
            step_run.status='failed'

            # pipeline_run status:
            pipeline_run.status="%s failed" % step.name
            pipeline_run.successful=False
            pipeline_run.finish_time=now

        session.commit()
