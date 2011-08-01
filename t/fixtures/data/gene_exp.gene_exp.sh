#!/bin/sh



python /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/provenance pipeline_start 1 1 -d

# step header:
echo step header 1>&2

echo
echo '****************************************************************'
echo starting gene_exp
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting gene_exp
date 1>&2
echo 1>&2


# exit script if any variable unset:
set -u


root_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq
programs=${root_dir}/programs
export PATH=/tools/bin:/hpc/bin:/bin:/usr/bin/:${root_dir}/programs
export PYTHONPATH=${PYTHONPATH:-}:${root_dir}/lib


# readset exports:
export org=None
export readlen=None
export working_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data
export reads_file=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data/gene_exp.diff.1K
export label=gene_exp
export ID=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data/gene_exp.diff.1K


cd ${working_dir}

exit_on_failure()
{
  retcode=$1
  pipelinerun_id=$2
  step_id=$3
  next_step_id=$4

  python ${root_dir}/bin/provenance mid_step ${pipelinerun_id} ${step_id} ${next_step_id} ${retcode} -d


  if [ $retcode != 0 ]; then
    echo step ${step_id} failed 1>&2
    exit $retcode
  else
    echo step ${step_id} passed 1>&2
  fi
}




# check success of step header:
exit_on_failure $? 1 1 2 -d
        
# step extract_significant:
echo step extract_significant 1>&2

grep 'yes$' ${ID} > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data/gene_exp.diff.1K.significant
        


# check success of step extract_significant:
exit_on_failure $? 1 2 3 -d
        
# step sort_by_name:
echo step sort_by_name 1>&2

sort -k3 ${ID}.significant > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data/gene_exp.diff.1K.sorted.name
        


# check success of step sort_by_name:
exit_on_failure $? 1 3 4 -d
        
# step sort_by_sample:
echo step sort_by_sample 1>&2

sort -k5,6 ${ID}.significant > /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/fixtures/data/gene_exp.diff.1K.sorted.sample
        


# check success of step sort_by_sample:
exit_on_failure $? 1 4 5 -d
        
# step footer:
echo step footer 1>&2
echo gene_exp done


# check success of step footer:
exit_on_failure $? 1 5 0 -d
        

python /proj/hoodlab/share/vcassen/rna-seq/rnaseq/bin/provenance pipeline_end 1 -d
