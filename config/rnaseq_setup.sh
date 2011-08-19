# add to PATH:
export PATH="${PATH}:/proj/hoodlab/share/programs/Rnaseq/bin"

# add to PYTHONPATH:
export PYTHONPATH="${PYTHONPATH:-}:/proj/hoodlab/share/programs/Rnaseq/lib:/proj/hoodlab/share/programs/Rnaseq/ext_libs"

# SGE
if [ -f /sge/aegir/common/settings.sh ]; then
   source /sge/aegir/common/settings.sh
fi
  
echo rnaseq_setup.sh done
