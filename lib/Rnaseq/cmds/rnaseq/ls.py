from Rnaseq import *
from Rnaseq.command import *
from RnaseqGlobals import *
from yaml import dump

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
        debug='debug' in os.environ or 'DEBUG' in os.environ
        
        # fixme: re-work the logic on this:
        # 'rnaseq ls --pr' ought to do the obvious thing.
        # Reverse order of determining what to do; empty case
        # should be what to do when you don't know what else to do.

        # get pipeline name; if none, ls all pipelines:
        pipeline_name=RnaseqGlobals.conf_value('pipeline_name') # set with -p option
        if not pipeline_name:
            self.ls_all_pipelines()
            return

        # get pipeline_run id; if none, ls all pipeline_run's for this pipeline:
        pipeline_run_id=RnaseqGlobals.conf_value('pipeline_run_id')
        if pipeline_run_id==None:
            if debug: print "looking for pipeline '%s'" % pipeline_name
            if re.match('\d+$',pipeline_name):
                pipeline=session.query(Pipeline).get(pipeline_name)
            else:
                pipeline=session.query(Pipeline).filter_by(name=pipeline_name).first()
            if pipeline==None:
                raise UserError("%s: no such pipeline" % pipeline_name)
            pipeline.__init__(readset=Readset(reads_file='dummy', label='dummy'))         # sqlalchemy doesn't call that for us???
            # but we need a dummy readset anyway
            pipeline.load_steps()
            self.ls_pipeline(pipeline)
            return

        user=RnaseqGlobals.conf_value('user')
        warn("user is %s" % user)
        pipeline_run=session.query(PipelineRun).filter_by(id=pipeline_run_id, user=user).first()
        if pipeline_run==None:
            raise UserError("no pipeline run with id=%s, user=%s" % (pipeline_run_id, user))
        self.ls_pipeline_run(pipeline_run)


    def ls_all_pipelines(self):
        session=RnaseqGlobals.get_session()
        pipelines=session.query(Pipeline).all()
        print "Available pipelines:"
        for p in pipelines:
            print "pipeline '%s' (%d)" % (p.name, p.id)

    def ls_pipeline(self,pipeline):
        print "pipeline: '%s'" % pipeline.name
        print "   description: %s" % pipeline.description
        print "   steps: %s" % ", ".join(pipeline.stepnames)
        
        user=RnaseqGlobals.conf_value('user')
        prs=[x for x in pipeline.pipeline_runs if x.user==user]
        s='' if len(prs)==1 else 's'
        print "%d run%s of %s" % (len(prs), s, pipeline.name)
        for pr in prs:
            if pr.user != user: continue
            print "\trun: %s" % pr.summary()


    def ls_pipeline_run(self,pipeline_run):
        print pipeline_run.report()

