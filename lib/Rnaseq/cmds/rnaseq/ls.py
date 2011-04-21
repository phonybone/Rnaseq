from Rnaseq import *
from Rnaseq.command import *
from RnaseqGlobals import *


class Ls(Command):

    def description(self):
        return "display information about pipelines"

    def usage(self):
        return "ls -p <pipeline> []"

    def run(self, *argv, **args):
        try:
            config=args['config']
            pipeline_name=config['pipeline_name']
        except KeyError as e:
            raise MissingArgError(str(e))
            
        try: argv=argv[0]
        except IndexError as e: raise ProgrammerGoof(e)

        session=RnaseqGlobals.get_session()


        # get pipeline name; if none, ls all pipelines:
        pipeline_name=RnaseqGlobals.conf_value('pipeline_name') # set with -p option
        if not pipeline_name:
            self.ls_all_pipelines()
            return

        # get pipeline_run id; if none, ls all pipeline_run's for this pipeline:
        pipeline_run_id=RnaseqGlobals.conf_value('pipeline_run_id')
        if pipeline_run_id==None:
            pipeline=session.query(Pipeline).filter_by(name=pipeline_name).first()
            if pipeline==None:
                raise UserError("%s: no such pipeline" % pipeline_name)
            self.ls_pipeline(pipeline)
            return

        pipeline_run=session.query(PipelineRun).filter_by(id=pipeline_run_id).first()
        if pipeline_run==None:
            raise UserError("no pipeline run with id=%s" % pipeline_run_id)
        self.ls_pipeline_run(pipeline_run)


    def ls_all_pipelines(self):
        session=RnaseqGlobals.get_session()
        pipelines=session.query(Pipeline).all()
        for p in pipelines:
            print "pipeline %s" % p.name

    def ls_pipeline(self,pipeline):
        print pipeline
        for pr in pipeline.pipeline_runs:
            print "%s" % pr

    def ls_pipeline_run(self,pipeline_run):
        print pipeline_run
        for sr in pipeline_run.step_runs:
            print sr
