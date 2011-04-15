#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import sys, yaml, subprocess, os

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class RunPipeline(Command):
    def usage(self):
        return "usage: run [output_file] -p <pipeline> -r <readset> [options]"

    def description(self):
        return "load and run a pipeline"
    
    def run(self, *argv, **args):
        try:
            config=args['config']
            readset_file=config['readset_file']
            pipeline_name=config['pipeline_name']
        except KeyError as e:
            raise MissingArgError(str(e))
            
        try:
            argv=argv[0]
        except IndexError as e:
            raise ProgrammerGoof(e)

        # Create the pipeline and readset objects:
        readset=Readset(filename=readset_file).load() 

        # Iterate through reads files defined in readset:
        # fixme: condense this loop
        for reads_path in readset.path_iterator():
            readset['reads_file']=reads_path
            pipeline=Pipeline(name=pipeline_name, readset=readset).load() # 
            pipeline.update(RnaseqGlobals.config)

            # Create the PipelineRun object:
            if True:
                pipeline_run=PipelineRun(pipeline)
                session=RnaseqGlobals.get_session()
                pipeline_run.start_time=int(time.time())
                pipeline_run.status='standby'
                session.add(pipeline_run)
                session.commit()
            
            # create and store the pipeline's shell script:
            script=pipeline.sh_script()
            script_filename=os.path.join(pipeline.working_dir(), pipeline.scriptname())
            try:
                os.makedirs(pipeline.working_dir())
            except OSError:
                pass                    # already exists, that's ok (fixme: could be permissions error)
            with open(script_filename, "w") as f:
                f.write(script)
                print "%s written" % script_filename

            # if running on the cluster, generate a calling (qsub) script and invoke that;
            out_filename=pipeline.out_filename()
            err_filename=pipeline.err_filename()
            if RnaseqGlobals.conf_value('use_cluster'):
                script_filename=pipeline.write_qsub_script(script_filename)
                cmd=self.qsub_launcher()
                output=sys.stdout
                err=sys.stderr
            else:
                # otherwise, just execute as a subprocess
                cmd=['sh']
                output=open(out_filename, 'w')
                err=open(err_filename, 'w')

            # create the cmd list:
            cmd.append(script_filename)
            print "launch cmd is '%s'" % " ".join(cmd)

            # launch the subprocess and check for success:
            if not RnaseqGlobals.conf_value('no_run'):
                pipe=subprocess.Popen(cmd, stdout=output, stderr=err)
                retcode=pipe.wait()
                if cmd[0]=="sh":
                    output.close()
                    err.close()
                    retcode=0   # why???
                if retcode != 0:
                    raise UserError("pipeline failed with return code %d\nsee %s.out and %s.err for diagnostics (in %s)" % \
                                        (retcode, pipeline.name, pipeline.name, pipeline.working_dir()))
                

    ########################################################################


    def qsub_launcher(self):
        # want to build list that looks like "ssh user@host /bin/qsub /working_dir/qsub_file
        launcher=[]
        launcher.append(RnaseqGlobals.conf_value('qsub','ssh_cmd'))

        user=RnaseqGlobals.conf_value('qsub','user') or os.environ['USER']
        host=RnaseqGlobals.conf_value('qsub','host')
        launcher.append("%s@%s" % (user,host))
                                   
        launcher.append(RnaseqGlobals.conf_value('qsub','exe'))
        return launcher

        

#print __file__, "checking in"
