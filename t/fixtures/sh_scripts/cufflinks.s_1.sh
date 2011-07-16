#!/bin/sh

# step header:

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


########################################################################
# step filterQuality:

perl ${programs}/filterQuality.pl -v -f ${format} -i ${ID}_1.${format} -o /dev/null -b ${ID}.qual_BAD_1.${format} 
rc=$?
if [ "$rc" != "0" ]; then
  echo filterQuality exiting on rc=$rc
  exit $rc
fi

perl ${programs}/filterQuality.pl -v -f ${format} -i ${ID}_2.${format} -o /dev/null -b ${ID}.qual_BAD_2.${format} 
rc=$?
if [ "$rc" != "0" ]; then
  echo filterQuality exiting on rc=$rc
  exit $rc
fi
echo filterQuality: done
date; echo

########################################################################
# step filterLowComplex:

perl ${programs}/filterLowComplex.pl -v -f ${format} -i ${ID}_1.${format} -o /dev/null -b ${ID}.complex_BAD_1.${format} 
rc=$?
if [ "$rc" != "0" ]; then
  echo filterLowComplex exiting on rc=$rc
  exit $rc
fi
perl ${programs}/filterLowComplex.pl -v -f ${format} -i ${ID}_2.${format} -o /dev/null -b ${ID}.complex_BAD_2.${format} 
rc=$?
if [ "$rc" != "0" ]; then
  echo filterLowComplex exiting on rc=$rc
  exit $rc
fi
echo filterLowComplex: done
date; echo


########################################################################
# step filterVectors:

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes

rm  -f ${ID}.vector_BAD.${format}
bowtie UniVec_Core --quiet -p 4  -k 1 -v 2 -q  -1 ${ID}_1.${format} -2 ${ID}_2.${format}| \
  perl -lane 'print unless($F[1] == 4)' > ${ID}.vector_BAD.${format}
rc=$?
if [ "$rc" != "0" ]; then
  echo filterVectors exiting on rc=$rc
  exit $rc
fi
echo filterVectors: done
date; echo




########################################################################
# step ribosomal_mit:

rm -f  ${ID}.riboMT_BAD.${format}
bowtie human.GRCh37.61.rRNA-MT --quiet -p 4 -k 1 -v 2 -q  -1 ${ID}_1.${format} -2 ${ID}_2.${format} | \
  perl -lane 'print unless($F[1] == 4)' > ${ID}.riboMT_BAD.${format}

rc=$?
if [ "$rc" != "0" ]; then
  echo ribosomal_mit exiting on rc=$rc
  exit $rc
fi
echo ribosomal_mit: done
date; echo


########################################################################
# step remove_erccs:

echo step remove_erccs 1>&2
export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
rm -f ${ID}.ercc_BAD.${format}
bowtie ERCC_reference_081215 --quiet -p 4 -k 1 -v 2 -q  -1 ${ID}_1.${format} -2 ${ID}_2.${format} | \
  perl -lane 'print unless($F[1] == 4)' > ${ID}.ercc_BAD.${format}
rc=$?
if [ "$rc" != "0" ]; then
  echo remove_erccs exiting on rc=$rc
  exit $rc
fi
echo remove_erccs: done
date; echo



########################################################################
# step repeats_consensus:

echo step repeats_consensus 1>&2
export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
rm -f  ${ID}.repeat_BAD.${format}
bowtie human_RepBase15.10 --quiet -p 4 -k 1 -v 2 -q  -1 ${ID}_1.${format} -2 ${ID}_2.${format} | \
  perl -lane 'print unless($F[1] == 4)' > ${ID}.repeat_BAD.${format}
rc=$?
if [ "$rc" != "0" ]; then
  echo repeats_consensus exiting on rc=$rc
  exit $rc
fi
echo repeats_consensus: done
date; echo


########################################################################
# step equalize:

perl ${programs}/removeBadReads.pl -v -paired ${ID}.qual_BAD_1.${format} ${ID}.qual_BAD_2.${format} ${ID}.complex_BAD_1.${format} ${ID}.complex_BAD_2.${format} ${ID}.vector_BAD.${format} ${ID}.riboMT_BAD.${format} ${ID}.ercc_BAD.${format} ${ID}.repeat_BAD.${format} - ${ID}_GOOD_1.${format} ${ID}_GOOD_2.${format}
rc=$?
if [ "$rc" != "0" ]; then
  echo step equalize exiting on rc=$rc
  exit $rc
fi
echo equalize: done
date; echo



#
# Replace the next two steps with tophat
# 

########################################################################
# step bowtie:

export BOWTIE_INDEXES=/proj/hoodlab/share/programs/bowtie-indexes
bowtie --sam --threads 4 --quiet -k 1 -v 2 -q hg19 -1 ${ID}_GOOD_1.${format} -2 ${ID}_GOOD_2.${format} ${ID}.bowtie.sam
rc=$?
if [ "$rc" != "0" ]; then
  echo main bowtie exiting on rc=$rc
  exit $rc
fi


echo bowtie: done
date; echo



########################################################################
# step sort and convert to sorted.bam format:

${programs}/samtools view -b -h -S -u ${ID}.bowtie.sam | ${programs}/samtools sort - ${ID}.sorted
rc=$?
if [ "$rc" != "0" ]; then
  echo samtools view/sort exiting on rc=$rc
  exit $rc
fi
echo sorting: done
date; echo


########################################################################
# step samtool copy:

${programs}/samtools view -h ${ID}.sorted.bam > ${ID}.sorted.sam



########################################################################
# step cufflinks:

ensembl=/proj/hoodlab/share/programs/Ensembl
RNAseq_Pi=/proj/hoodlab/share/vcassen/rna-seq/RNAseq-Pi/data/fasta
mask_file=${ensembl}/Homo_sapiens.GRCh37.62.PSEUDO.corr.gtf
gtf_guide=${ensembl}/Homo_sapiens.GRCh37.62.corr.gtf
bias_correct=${ensembl}/hg19_exp.fa
NPROC=6

${programs}/cufflinks -o ${ID}.cufflinks -p ${NPROC} --frag-bias-correct ${bias_correct} -u -g ${gtf_guide} -M ${mask_file} ${ID}.sorted.bam

rc=$?
if [ "$rc" != "0" ]; then
  echo cufflinks exiting on rc=$rc
  exit $rc
fi
echo cufflinks: done
date; echo

########################################################################

# step  footer:

echo done
