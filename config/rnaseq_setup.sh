# add to PATH:
export PATH="${PATH}:/proj/hoodlab/share/vcassen/rna-seq/Rnaseq/bin"

# add to PYTHONPATH:
export PYTHONPATH="${PYTHONPATH:-}:/proj/hoodlab/share/vcassen/rna-seq/rnaseq/lib:/proj/hoodlab/share/vcassen/lib/python"

# SGE
if [ -f /sge/aegir/common/settings.sh ]; then
   source /sge/aegir/common/settings.sh
fi
  
echo rnaseq_setup.sh done
