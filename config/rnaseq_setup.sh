# add to PATH:
export PATH="${PATH}:/proj/hoodlab/share/programs/Rnaseq/bin"

# SGE
if [ -f /sge/aegir/common/settings.sh ]; then
   source /sge/aegir/common/settings.sh
fi
  
echo rnaseq_setup.sh done
