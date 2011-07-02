from Rnaseq import *

class header(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='header'
        self.force=True
        self.skip_success_check=True

    def usage(self, context):
        template='''
# header
echo
echo '****************************************************************'
echo starting ${pipeline.name}
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting ${pipeline.name}
date 1>&2
echo 1>&2


# exit script if any variable unset:
set -u


export PATH=${config['rnaseq']['path']}
export PYTHONPATH=$${PYTHONPATH}:${config['rnaseq']['root_dir']}/lib

root_dir=${root_dir}
programs=${programs}
reads_file=${reads_file}
ID=${ID}
working_dir=${working_dir}

cd $${working_dir}

exit_on_failure()
{
  retcode=$$1
  pipelinerun_id=$$2
  step_id=$$3
  next_step_id=$$4

  python ${config['rnaseq']['root_dir']}/bin/provenance mid_step $${pipelinerun_id} $${step_id} $${next_step_id} $${retcode}


  if [ $$retcode != 0 ]; then
    echo $${last_step} failed 1>&2
    exit $$retcode
  else
    echo $${last_step} passed 1>&2
  fi
}

        '''
        restore_indent=True
        return template
        
