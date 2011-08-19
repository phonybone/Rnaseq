#!/bin/tcsh

# add to PATH:
setenv PATH "${PATH}:/proj/hoodlab/share/vcassen/rna-seq/Rnaseq/bin"
rehash

# add to PYTHONPATH:
if ( $?PYTHONPATH ) then
    setenv PYTHONPATH "${PYTHONPATH}:/proj/hoodlab/share/programs/Rnaseq/lib:/proj/hoodlab/share/programs/Rnaseq/ext_libs"
else
    setenv PYTHONPATH "/proj/hoodlab/share/programs/Rnaseq/lib:/proj/hoodlab/share/programs/Rnaseq/ext_libs"
endif

# SGE
if ( -f /sge/aegir/common/settings.csh ) then
   source /sge/aegir/common/settings.csh
endif

  
