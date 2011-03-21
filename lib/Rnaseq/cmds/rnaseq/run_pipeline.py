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
    
    def run(self, **args):
        try:
            argv=args['argv']          
            readset_name=Rnaseq.options.readset_name
            pipeline_name=Rnaseq.options.pipeline_name
            if readset_name==None or pipeline_name==None:
                raise UserError(Rnaseq.usage)

            readset=Readset(name=readset_name).load() 
            pipeline=Pipeline(name=pipeline_name, readset=readset).load()
            pipeline.update(Rnaseq.config)
            # code up to this point copied verbatim from load.py; would be nice if one command could call another?
            # and if commands could return values...
            
            # create and store the pipeline's shell script:
            # taken from code in shell_script.py...
            script=pipeline.sh_script()
            script_filename=os.path.join(pipeline.working_dir(),Rnaseq.options.pipeline_scriptname)
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
            if Rnaseq.options.use_cluster:
                script_filename=pipeline.write_qsub_script(script_filename, out_filename, err_filename)
                launcher=Rnaseq.config['qsub']['exe']
                print "qsub_filename is %s" % script_filename
            else:
                # otherwise, just execute as a subprocess
                launcher='sh'
                output=open(out_filename, 'w')
                err=open(err_filename, 'w')


            cmd=[launcher, script_filename]
            print "about to '%s' (not)" % " ".join(cmd)
            #pipe=subprocess.Popen(cmd, stdout=output, stderr=err)
            #retcode=pipe.wait()
            if launcher="sh":
                output.close()
                err.close()
            retcode=0
            if retcode != 0:
                raise UserError("pipeline failed with return code %d\nsee %s.out and %s.err for diagnostics (in %s)" % \
                                (retcode, pipeline.name, pipeline.name, pipeline.working_dir()))
            

        except KeyError as e:
            raise MissingArgError(str(e))
        except IndexError as e:
            raise UserError("Missing args in load")

#print __file__, "checking in"
