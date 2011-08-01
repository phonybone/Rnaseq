#!/bin/sh



echo
echo '****************************************************************'
echo starting filter
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting filter
date 1>&2
echo 1>&2


# exit script if any variable unset:
set -u


root_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq
programs=${root_dir}/programs
export PATH=/tools/bin:/hpc/bin:/bin:/usr/bin/:${root_dir}/programs
export PYTHONPATH=${PYTHONPATH}:${root_dir}/lib


# readset exports:
export org=mouse
export readlen=75
export working_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/working_dir
export reads_file=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/s_1_export.txt
export label=readset1
export format=txt
export ID=/proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/working_dir/s_1_export.txt


cd ${working_dir}

exit_on_failure()
{
  retcode=$1
  pipelinerun_id=$2
  step_id=$3
  next_step_id=$4

  python ${root_dir}/bin/provenance mid_step ${pipelinerun_id} ${step_id} ${next_step_id} ${retcode}


  if [ $retcode != 0 ]; then
    echo ${last_step} failed 1>&2
    exit $retcode
  else
    echo ${last_step} passed 1>&2
  fi
}


ln -s /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/s_1_export.txt_1.txt /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/working_dir/s_1_export.txt

# step export2fq:
echo step export2fq 1>&2

format=fq

perl ${programs}/fq_all2std.py solexa2fastq ${ID} ${ID}.${format}
            

# step filterQuality:
echo step filterQuality 1>&2

perl ${programs}/filterQuality.pl -v -f ${format} -i ${ID}.${format} -o /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/working_dir/s_1_export.txt.qual_OK.${format} -b /proj/hoodlab/share/vcassen/rna-seq/rnaseq/t/run_pipeline/working_dir/s_1_export.txt.qual_BAD.${format}
            

# step filterLowComplex:
echo step filterLowComplex 1>&2

perl ${programs}/filterLowComplex.pl -v -f ${format} -i ${ID}.${format} -o ${ID}.complex_OK.${format} -b ${ID}.complex_BAD.${format}
            

# step ribosomal_mit:
echo step ribosomal_mit 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie human.GRCh37.61.rRNA-MT --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q ${ID}.${format} | perl -lane 'print unless($F[1] == 4)' > ${ID}.readset1.syml_BAD.${format}


# step remove_erccs:
echo step remove_erccs 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie ERCC_reference_081215 --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q ${ID}.${format} | perl -lane 'print unless($F[1] == 4)' > ${ID}.readset1.syml_BAD.${format}

