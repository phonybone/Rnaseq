#!/bin/tcsh

# add to PATH:
setenv PATH "${PATH}:/proj/hoodlab/share/vcassen/rna-seq/Rnaseq/bin"
rehash

# add to PYTHONPATH:
if ( $?PYTHONPATH ) then
    setenv PYTHONPATH "${PYTHONPATH}:/proj/hoodlab/share/vcassen/rna-seq/Rnaseq/lib:/proj/hoodlab/share/vcassen/lib/python"
else
    setenv PYTHONPATH "/proj/hoodlab/share/vcassen/rna-seq/Rnaseq/lib:/proj/hoodlab/share/vcassen/lib/python"
endif

# SGE
if ( -f /sge/aegir/common/settings.sh ) then
   source /sge/aegir/common/settings.sh
endif

  
