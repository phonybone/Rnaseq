#!/bin/sh

# header:
root_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq

export PATH=/tools/bin:/hpc/bin:/bin:/usr/bin/:${root_dir}/programs
export PYTHONPATH=${PYTHONPATH}:/proj/hoodlab/share/vcassen/rna-seq/rnaseq/lib

programs=${root_dir}/programs
reads_file=/proj/hoodlab/share/vcassen/rna-seq/qiang_data/s_1
ID=/proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1/s_1
format=fq
readlen=101

########################################################################
exit_on_failure()
{
  retcode=$1
  pipelinerun_id=$2
  step_id=$3
  next_step_id=$4

  python /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/provenance mid_step ${pipelinerun_id} ${step_id} ${next_step_id} ${retcode}


  if [ "$retcode" != "0" ]; then
    echo ${last_step} failed 1>&2
    exit $retcode
  else
    echo ${last_step} passed 1>&2
  fi
}

ln -s ${reads_file}_1.${format} ${ID}_1.${format}
ln -s ${reads_file}_2.${format} ${ID}_2.${format}
