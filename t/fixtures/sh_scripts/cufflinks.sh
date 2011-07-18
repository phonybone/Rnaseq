#!/bin/sh



echo
echo '****************************************************************'
echo starting cufflinks
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting cufflinks
date 1>&2
echo 1>&2


# exit script if any variable unset:
set -u


root_dir=/proj/hoodlab/share/vcassen/rna-seq/rnaseq
export PATH=/tools/bin:/hpc/bin:/bin:/usr/bin/:${root_dir}/programs
export PYTHONPATH=${PYTHONPATH}:${root_dir}/lib

programs=${root_dir}/programs
reads_file=/proj/hoodlab/share/vcassen/rna-seq/qiang_data/s_1_1_sequence.txt
ID=/proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1
working_dir=/proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq

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


ln -s /proj/hoodlab/share/vcassen/rna-seq/qiang_data/s_1_1_sequence.txt_1.fq /proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1_1.fq
ln -s /proj/hoodlab/share/vcassen/rna-seq/qiang_data/s_1_1_sequence.txt_2.fq /proj/hoodlab/share/vcassen/rna-seq/qiang_data/rnaseq/s_1_2.fq

# step filterQuality:
echo step filterQuality 1>&2

perl ${programs}/filterQuality.pl -v -f fq -i ${ID}_1.${format} -o /dev/null -b ${ID}.qual_BAD_1.fq
perl ${programs}/filterQuality.pl -v -f fq -i ${ID}_2.${format} -o /dev/null -b ${ID}.qual_BAD_2.fq
            

# step filterLowComplex:
echo step filterLowComplex 1>&2

perl ${programs}/filterLowComplex.pl -v -f fq -i ${ID}_1.${format} -o ${ID}.complex_OK_1.fq -b ${ID}.complex_BAD_1.fq
perl ${programs}/filterLowComplex.pl -v -f fq -i ${ID}_2.${format} -o ${ID}.complex_OK_2.fq -b ${ID}.complex_BAD_2.fq
            

# step filterVectors:
echo step filterVectors 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie UniVec_Core -1 ${ID}_1.${format} -2 ${ID}_2.${format} --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q | perl -lane 'print unless($F[1] == 4)' > ${ID}.filterVectors_BAD.fq


# step ribosomal_mit:
echo step ribosomal_mit 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie human.GRCh37.61.rRNA-MT -1 ${ID}_1.${format} -2 ${ID}_2.${format} --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q | perl -lane 'print unless($F[1] == 4)' > ${ID}.ribosomal_mit_BAD.fq


# step remove_erccs:
echo step remove_erccs 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie ERCC_reference_081215 -1 ${ID}_1.${format} -2 ${ID}_2.${format} --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q | perl -lane 'print unless($F[1] == 4)' > ${ID}.remove_erccs_BAD.fq


# step repeats_consensus:
echo step repeats_consensus 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie human_RepBase15.10 -1 ${ID}_1.${format} -2 ${ID}_2.${format} --quiet -p 4 -S --sam-nohead -k 1 -v 2 -q | perl -lane 'print unless($F[1] == 4)' > ${ID}.repeats_consensus_BAD.fq


# step equalize:
echo step equalize 1>&2

perl ${programs}/removeBadReads.pl -v -paired ${ID}.qual_BAD_1.${format} ${ID}.qual_BAD_1.${format} ${ID}.complex_BAD_1.${format} ${ID}.complex_BAD_1.${format} ${ID}.vector_BAD.${format} ${ID}.riboMT_BAD.${format} ${ID}.remove_erccs_BAD.${format} ${ID}.repeats_BAD.${format} - ${ID}_GOOD_1.fq ${ID}_GOOD_2.fq


# step bowtie:
echo step bowtie 1>&2

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie   --quiet -k 1 -v 2 -q hg19 -1 $${ID}_GOOD_1.${format} -2 $${ID}_GOOD_2.${format} 


# step bowtie2bam:
echo step bowtie2bam 1>&2

${programs}/samtools view -b -h -S -u ${ID}.bowtie.sam | ${programs}/samtools sort - ${ID}.sorted


# step samtool_copy:
echo step samtool_copy 1>&2

${programs}/samtools view -h ${ID}.sorted.bam > ${ID}.sorted.sam


# step cufflinks:
echo step cufflinks 1>&2

ensembl=/proj/hoodlab/share/programs/Ensembl
mask_file=${ensembl}/Homo_sapiens.GRCh37.62.PSEUDO.corr.gtf
gtf_guide=${ensembl}/Homo_sapiens.GRCh37.62.corr.gtf
bias_correct=${ensembl}/hg19_exp.fa

${programs}/cufflinks -o ${ID}.cufflinks  --frag-bias-correct ${bias_correct} -u -g ${gtf_guide} -M ${mask_file} ${ID}.sorted.bam
        

# step footer:
echo step footer 1>&2
echo cufflinks done
