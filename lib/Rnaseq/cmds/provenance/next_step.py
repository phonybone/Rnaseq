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

        # get pipeline_run object, then pipeline object:
        pipeline_run=session.query(PipelineRun).filter_by(id=pipelinerun_id).first()
        if pipeline_run==None:
            raise UserError("No pipeline run for pipelinerun_id=%s" % pipelinerun_id)
        pipeline=session.query(Pipeline).filter_by(id=pipeline_run.pipeline_id).first()
        if pipeline==None:
            raise UserError("No pipeline for pipeline_id=%s" % pipeline_run.pipeline_id)


        last_step_run=session.query(StepRun).filter_by(pipeline_run_id=pipeline_run.id, name=last_stepname).first()
        if not last_step_run:
            print "no last step_run???"
            return
        
        now=time.time
        if retcode==0:                   # last step was a success!
            # set last step status:
            last_step_run.successful=True
            last_step_run.finish_time=now
            last_step_run.status='finished' # or something...

            # set pipeline_run status:
            pipeline_run.status="%s finished" % last_stepname

            # Create new step_run object and insert it (unless this is the last step, excluding footer)
            next_step=session.query(Step).filter_by(name=pipeline.stepAfter(last_stepname).name).first()
            if next_step:
                next_step_run=StepRun(step_id=next_step.id, pipeline_run_id=pipeline_run.id, start_time=now, status='started')
                session.add(next_step_run)

        else:                           # last step failed (boo)
            last_step_run.successful=False
            last_step_run.finish_time=now
            last_step_run.status='failed'

            # pipeline_run status:
            pipeline_run.status="%s failed" % last_stepname
            pipeline_run.successful=False
            pipeline_run.finish_time=now

        session.commit()
        





        session.commit()



