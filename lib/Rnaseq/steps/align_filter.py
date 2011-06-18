from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals

class align_filter(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

        try: aligner=kwargs['aligner']
        except: aligner=RnaseqGlobals.conf_value('rnaseq','aligner')
        self.aligner(aligner)

    def aligner(self,*args):
        try: self.__aligner__=args[0]
        except: pass

        aligner=self.__aligner__
        if aligner=='bowtie':
            self.usage='%(exe)s %(ewbt)s %(args)s --un %(output)s %(input)s'
            self.exe='bowtie'
            self.sh_template='bowtie_filter.tmpl'
            self.args='--quiet -p 4 -S --sam-nohead -k 1 -v 2 -q'
        elif aligner=='blat':
            self.usage='%(exe)s %(blat_index)s %(input)s %(args)s %(psl)s'
            self.exe='blat'
            self.sh_template='blat_filter.tmpl'
            self.args='-fastMap -q=DNA -t=DNA'
        else:
            raise UserError("unknown aligner '%s'" % aligner)
        
        return aligner
    
    def sh_cmd(self):
        if self.aligner=='bowtie':
            try: paired_reads=self.pipeline.readset.paired_reads
            except AttributeError: paired_reads=False
            if paired_reads:
                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
${exe} ${ewbt} -1 ${input[0]} -2 ${input[1]} ${args} --un ${output}  | perl -lane 'print unless($$F[1] == 4)' > ${filtered}
                '''
                restore_indent=True
            else:
                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
${exe} ${ewbt} ${args} --un ${output} ${input} | perl -lane 'print unless($$F[1] == 4)' > ${filtered}
                '''
                restore_indent=True

                

        elif self.aligner=='blat':
            pass
        else:
            raise ConfigError("Unknown alignment program '%s'" % self.aligner)
