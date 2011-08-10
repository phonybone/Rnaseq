from RnaseqGlobals import *
from Rnaseq import *

def run_pipeline(pipeline):
    cf=CmdFactory(program='rnaseq')
    cf.add_cmds(RnaseqGlobals.conf_value('rnaseq','cmds'))
    cmd=cf.new_cmd('run')
    argv=[]
    cmd.run(argv, config=RnaseqGlobals.config)

    (pipeline_run, step_runs)=pipeline.make_run_objects(session)
    script_filename=pipeline.write_sh_script(pipeline_run=pipeline_run, step_runs=step_runs) 

    cmd=['sh', script_filename]
    pipe=subprocess.Popen(cmd)
    retcode=pipe.wait()
    return retcode
