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
            self.exe='bowtie'
            self.args='--quiet -p 4 -S --sam-nohead -k 1 -v 2 -q'
        elif aligner=='blat':
            self.exe='blat'
            self.args='-fastMap -q=DNA -t=DNA'
        else:
            raise UserError("unknown aligner '%s'" % aligner)
        
        return aligner
    
    # fixme: usage in progress, ill-formed
    def usage(self):
        if self.aligner=='bowtie':
            if self.paired_reads:

                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
bowtie ${ewbt} -1 ${ID}_1.${format} -2 ${ID}_2.${format} ${args} --un ${output}  | perl -lane 'print unless($$F[1] == 4)' > ${filtered}
                ''' % ()

                context.outputs=["%s.qual_OK.%s" % (context.ID, context.format)]
                context.creates=["%s.qual_BAD.%s" % (context.ID, context.format)]

            else:
                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
bowtie ${ewbt} ${args} --un ${output} ${input} | perl -lane 'print unless($$F[1] == 4)' > ${filtered}
                '''
                restore_indent=True

                

        elif self.aligner=='blat':
            pass
        else:
            raise ConfigError("Unknown alignment program '%s'" % self.aligner)
