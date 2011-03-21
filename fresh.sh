#!/bin/sh

# header
echo header step
export PATH=/tools/bin
export BOWTIE_INDEX=/jdrf/data_var/solexa/genomes/mouse


# export2fq
echo export2fq step
perl fq_all2std.pl solexa2fastq /users/vcassen/links/samples/sandbox/s_6_export.1K.txt /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.fq

# check success of step export2fq:
retcode=$?
if [ $retcode != 0 ]; then
  echo export2fq failed
  python provenance update -p 'filters_only' --status 'failed in step export2fq'
  exit $retcode
fi
python provenance insert /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.fq fq_all2std.pl 

# filterQuality
echo filterQuality step
perl filterQuality.pl -v -i /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.fq -o /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.qual_OK.fq -b /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.bowtie_qual_BAD.fq

# check success of step filterQuality:
retcode=$?
if [ $retcode != 0 ]; then
  echo filterQuality failed
  python provenance update -p 'filters_only' --status 'failed in step filterQuality'
  exit $retcode
fi
python provenance insert /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.qual_OK.fq filterQuality.pl 

# filterLowComplex
echo filterLowComplex step
perl filterLowComplex.pl -v -i /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.vector_OK.fq -o /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.complex_OK.fq -b /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.bowtie_complex_BAD.fq

# check success of step filterLowComplex:
retcode=$?
if [ $retcode != 0 ]; then
  echo filterLowComplex failed
  python provenance update -p 'filters_only' --status 'failed in step filterLowComplex'
  exit $retcode
fi
python provenance insert /users/vcassen/links/samples/sandbox/s_6_export.1K.txt.complex_OK.fq filterLowComplex.pl 

python provenance update -p filters_only --status finished 
