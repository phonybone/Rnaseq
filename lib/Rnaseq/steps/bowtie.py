from Rnaseq import *

class bowtie(Step):
    defaults={'args': '--quiet -k 1 -v 2 -q',
              'threads': 1,
              'output_file': '',
              'output_format': 'bowtie'}

    def usage(self,context):
        paired=self.paired_end()
        if paired:
            inputs='-1 ${inputs[0]} -2 ${inputs[1]}'
        else:
            inputs='${inputs[0]}'

        args=self.args
        if self.output_format == 'bowtie':
            output_file=self.output_file
            format=''
        elif self.output_format == 'sam':
            format='--sam'
            output_file='$${ID}.%s.sam' % self.name # '$$' because ID gets interpolated in step.sh_script()
        else:
            raise ConfigError("step %s: unknown output bowtie format '%s'" % (self.name, self.output_format))
            
        threads=('--threads %d' % self.threads) if self.threads != 1 else ''
            
        usage='''
export BOWTIE_INDEXES=${bowtie_index}
bowtie %(format)s %(threads)s ${args} ${ewbt} %(input)s %(output_file)s
''' % {'format':format, 'threads':threads, 'input' : inputs, 'output_file' : output_file}

        return usage

    def output_list(self):
        output='${ID}.%s.%s' % (self.name, self.output_format)
        return [output]
