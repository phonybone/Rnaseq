#-*-python-*-
from warn import *
from Rnaseq import *
from Rnaseq.command import *
import sys, yaml, subprocess, os

# usage: provenance load <readset pipeline>
# This is sort of a test command, probably won't be used in production

class RunPipeline(Command):
    def description(self):
        return "load and run a pipeline"
    
    def run(self, *argv, **args):
        try:
            argv=args['argv']          
            options=args['options']
        except KeyError as e:
            raise MissingArgError(str(e))
        except IndexError as e:
            raise UserError("Missing args in load")

        try:
            readset_name=options.readset_name
            pipeline_name=options.pipeline_name
            if readset_name==None or pipeline_name==None:
                raise UserError(RnaseqGlobals.usage)
            
            readset=Readset(name=readset_name).load() 
            pipeline=Pipeline(name=pipeline_name, readset=readset).load()
            pipeline.update(RnaseqGlobals.config)
            # code up to this point copied verbatim from load.py; would be nice if one command could call another?
            # and if commands could return values...
            
            # create and store the pipeline's shell script:
            # taken from code in shell_script.py...
            script=pipeline.sh_script()
            script_filename=os.path.join(pipeline.working_dir(), pipeline.scriptname())
            try:
                os.makedirs(pipeline.working_dir())
            except OSError:
                pass                    # already exists, that's ok (fixme: could be permissions error)
            with open(script_filename, "w") as f:
                f.write(script)
                warn("%s written" % script_filename)

            # if running on the cluster, generate a calling (qsub) script and invoke that;
            out_filename=pipeline.out_filename()
            err_filename=pipeline.err_filename()
            if options.use_cluster:
                script_filename=pipeline.write_qsub_script(script_filename)
                cmd=self.qsub_launcher()
                output=sys.stdout
                err=sys.stderr
            else:
                # otherwise, just execute as a subprocess
                cmd=['sh']
                output=open(out_filename, 'w')
                err=open(err_filename, 'w')


            cmd.append(script_filename)
            print "launch cmd is '%s'" % " ".join(cmd)

            pipe=subprocess.Popen(cmd, stdout=output, stderr=err)
            retcode=pipe.wait()
            if cmd[0]=="sh":
                output.close()
                err.close()
            retcode=0
            if retcode != 0:
                raise UserError("pipeline failed with return code %d\nsee %s.out and %s.err for diagnostics (in %s)" % \
                                (retcode, pipeline.name, pipeline.name, pipeline.working_dir()))

        except DummyException as de:
            pass


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
