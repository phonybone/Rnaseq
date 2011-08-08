from Rnaseq import *

class bowtie(Step):
    required_attrs=['bowtie_index', 'ewbt', 'args', 'output_format']
    defaults={'args': '--quiet -k 1 -v 2 -q',
              'output_format': 'bowtie'}

    
    def __init__(self,*args,**kwargs):
        Step.__init__(self,*args,**kwargs)

    def usage(self,context):
        paired=self.paired_end()
        if paired:
            inputs='-1 ${inputs[0]} -2 ${inputs[1]}'
        else:
            inputs='${inputs[0]}'

        args=self.args

        # set output_format:
        if self.output_format == 'bowtie':
            output_file='$${ID}.%s.bowtie' % self.name
            format=''
        elif self.output_format == 'sam':
            format='--sam'
            output_file='$${ID}.%s.sam' % self.name # '$$' because ID gets interpolated in step.sh_script()
        else:
            raise ConfigError("step %s: unknown output bowtie format '%s'" % (self.name, self.output_format))
            
        # try to set bowtie_index if needed:
        if not hasattr(self, 'bowtie_index'):
            try:
                self.bowtie_index=self.pipeline.readset.bowtie_index
                #print "got bowtie_index from readset"
            except:
                #print "no 'bowtie_index' in readset"
                pass

        if not hasattr(self, 'bowtie_index'):
            try:
                self.bowtie_index=self.pipeline['bowtie_index']
                #print "got bowtie_index from pipeline"
            except:
                #print "no 'bowtie_index' in pipeline"
                pass

        if not hasattr(self, 'bowtie_index'):
            self.bowtie_index=RnaseqGlobals.conf_value('rnaseq', 'bowtie_index')
            #print "got bowtie_index from RnaseqGlobals"
        else:
            #print "bowtie had index=%s" % self.bowtie.index
            pass
        
        # set threads:
        if hasattr(self, 'threads'):
            threads='--threads %s' % self.threads
        else:
            threads='--threads' % RnaseqGlobals.conf_value('qsub', 'nprocs')

        # set ewbt if necessary:
        if not hasattr(self, 'ewbt'):
            try: self.ewbt=self.pipeline.readset.ewbt
            except: pass

        if not hasattr(self,'ewbt'):
            try:
                org=self.pipeline.readset.org.lower()
                org={'human':'human', 'hs':'human',
                     'mouse':'mouse', 'mm':'mouse'}[org]
                self.ewbt={'human':'hg19',
                           'mouse':'mm37.61'}[org]
            except: pass

        usage='''
export BOWTIE_INDEXES=${bowtie_index}
bowtie %(format)s %(threads)s ${args} ${ewbt} %(input)s %(output_file)s
''' % {'format':format, 'threads':threads, 'input' : inputs, 'output_file' : output_file}

        return usage

    def output_list(self,*args):
        output='${ID}.%s.%s' % (self.name, self.output_format)
        return [output]
