from Rnaseq import *

class header(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='header'
        self.force=True
        self.skip_success_check=True

    def usage(self, context):
        path=RnaseqGlobals.conf_value('rnaseq','path')

        readset=self.pipeline.readset
        export_block=''
        for attr in readset.exports:
            try: export_block+="export %s=%s\n" % (attr, getattr(readset, attr))
            except AttributeError: pass
        
        template='''
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


root_dir=${root_dir}
programs=$${root_dir}/programs
export PATH=%(path)s:$${root_dir}/programs
export PYTHONPATH=$${PYTHONPATH}:$${root_dir}/lib


# readset exports:
%(readset_exports)s

cd $${working_dir}

exit_on_failure()
{
  retcode=$$1
  pipelinerun_id=$$2
  step_id=$$3
  next_step_id=$$4

  python $${root_dir}/bin/provenance mid_step $${pipelinerun_id} $${step_id} $${next_step_id} $${retcode}


  if [ $$retcode != 0 ]; then
    echo $${last_step} failed 1>&2
    exit $$retcode
  else
    echo $${last_step} passed 1>&2
  fi
}

''' % {'path':path, 'readset_exports':export_block}
        restore_indent=True

        if self.paired_end():
            template+='''
ln -s ${reads_file}_1.${format} ${ID}_1.${format}
ln -s ${reads_file}_2.${format} ${ID}_2.${format}
'''
        else:
            template+='''
ln -s ${reads_file}_1.${format} ${ID}
'''
            
        return template
        
    ########################################################################

    def output_list(self):
        if self.paired_end():
            return ['${ID}_1.${format}', '${ID}_2.${format}']
        else:
            return ['${ID}']
