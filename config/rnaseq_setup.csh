#!/bin/tcsh

# add to PATH:
setenv PATH "${PATH}:/proj/hoodlab/share/programs/Rnaseq/bin"
rehash

# SGE
if ( -f /sge/aegir/common/settings.csh ) then
   source /sge/aegir/common/settings.csh
endif

  
