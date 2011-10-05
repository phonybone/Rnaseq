from Rnaseq import *
import re

class header(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='header'
        self.force=True
        self.skip_success_check=False

    def usage(self, context):
        path=RnaseqGlobals.conf_value('rnaseq','path')

        readset=self.pipeline.readset
        export_block=''
        for attr in readset.exports:
            try: export_block+="export %s=%s\n" % (attr, getattr(readset, attr))
            except AttributeError: pass

        if RnaseqGlobals.conf_value('debug'): self.debug='-d'
        else: self.debug=''
        
        template='''
echo
echo '****************************************************************'
echo starting ${pipeline.name}
date
echo

echo 1>&2
echo 1>&2 '****************************************************************'
echo 1>&2 starting ${pipeline.name}
date 1>&2
echo 1>&2


# exit script if any variable unset:
set -u


root_dir=${root_dir}
programs=$${root_dir}/programs
export PATH=%(path)s:$${root_dir}/programs
export PYTHONPATH=$${PYTHONPATH:-}:$${root_dir}/lib:$${root_dir}/ext_libs


# readset exports:
%(readset_exports)s

cd $${working_dir}

exit_on_failure()
{
  retcode=$$1
  pipelinerun_id=$$2
  step_id=$$3
  next_step_id=$$4

  python $${root_dir}/bin/provenance mid_step $${pipelinerun_id} $${step_id} $${next_step_id} $${retcode} ${debug}


  if [ $$retcode != 0 ]; then
    echo step $${step_id} failed 1>&2
    exit $$retcode
  else
    echo step $${step_id} passed 1>&2
  fi
}

''' % {'path':path, 'readset_exports':export_block}
        restore_indent=True

        # add link part if necessary:
        # Is necessary if original location of data is different from working_dir:

        # create code to link input files to working_dir files if necessary;
        link_part=''
        if os.path.dirname(readset.reads_files[0]) != readset.working_dir:
            lts=self.link_targets()
            for rf,target in lts.items():
                link_cmd="ln -fs %s %s\n" % (rf, os.path.join(readset.working_dir,target))
                link_part+=link_cmd
        template+=link_part
            
        return template



    def link_targets(self):
        try: return self._link_targets
        except AttributeError: pass
        
        readset=self.pipeline.readset
        self._link_targets={}
        try: format=readset.format
        except AttributeError: format=None

        for rf in readset.reads_files:
            if hasattr(readset, 'ID'):
                target=readset.ID
                if self.paired_end():
                    mg=re.search('(_\d)\.', rf)
                    if not mg:
                        raise ConfigError("malformed read_file for paired_end dataset: %s" % rf)
                    target+=mg.group(1)
                target=os.path.basename(target)
            else:
                target=os.path.basename(rf)
                print "No ID defined in readset"
                    
            if format:
                if re.search('\.\w$', target):
                    target=re.sub('\.\w+$', '.'+format, target) # change extension if necessary
                else:
                    target+=".%s" % format # just append format
                    
            self._link_targets[rf]=target

        return self._link_targets
        
    ########################################################################

    # This shouldn't call self.input_list(), because it sets up a circular dependency
    # in conjunction with pipeline.convert_io().  
    def output_list(self,*args):
        readset=self.pipeline.readset
        working_dir=readset.working_dir
        lts=[os.path.join(working_dir,t) for t in self.link_targets().values()]
        lts.sort()
        return lts
        
