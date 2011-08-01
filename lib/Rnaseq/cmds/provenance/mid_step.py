#-*-python-*-
import time, yaml

from warn import *
from Rnaseq import *
from Rnaseq.command import *

class MidStep(Command):
    def usage(self):
        return "usage: mid_step <pipelinerun_id> <steprun_id> <next_steprun_id> <retcode>"

    def description(self):
        return "record provenance when one step finishes and the next begins"

    def run(self, *argv, **args):
        try:
            config=args['config']
            (pipelinerun_id, steprun_id, next_steprun_id, retcode)=[int(x) for x in argv[0][2:6]]
            
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
        step_name=step_run.step_name

        # get pipeline and step:
#         pipeline=session.query(Pipeline).get(pipeline_run.pipeline_id)
#         step_factory=StepFactory(pipeline)
#         step=step_factory.new_step(step_name)
        
        
        now=int(time.time())
        if retcode==0:                   # last step was a success!
            # set last step status:
            step_run.successful=True
            step_run.finish_time=now
            step_run.status='finished' # or something...

            # report on created files:
            for o in step_run.file_outputs:
                print "%s: %s created" % (step_run.step_name, o.path)

            # set the start time for the next step_run:
            if next_steprun_id > 0:
                next_steprun=session.query(StepRun).filter_by(id=next_steprun_id).first()
                next_steprun.start_time=now
                next_steprun.status='started'

                pipeline_run.status="%s started" % next_steprun.step_name
                pipeline_run.current_step_run_id=next_steprun_id

            else:
                pipeline_run.status="%s finished" % step_name
                #pipeline_run.current_step_run_id=0 # let the last step id stand for reporting purposes

        else:                           # last step failed (boo)
            step_run.successful=False
            step_run.finish_time=now
            step_run.status='failed'

            # pipeline_run status:
            pipeline_run.status="%s failed" % step_name
            pipeline_run.successful=False
            pipeline_run.finish_time=now

        session.commit()
