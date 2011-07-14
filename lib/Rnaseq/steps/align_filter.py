from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals

class align_filter(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

        try: aligner=kwargs['aligner']
        except: aligner=RnaseqGlobals.conf_value('rnaseq','aligner')
        self.set_aligner(aligner)

    def set_aligner(self,*args):
        try: self.aligner=args[0]
        except: pass

        aligner=self.aligner
        if aligner=='bowtie':
            self.exe='blat'
            self.args='--quiet -p 4 -S --sam-nohead -k 1 -v 2 -q'
        elif aligner=='blat':
            self.exe='blat'
            self.args='-fastMap -q=DNA -t=DNA'
        else:
            raise UserError("unknown aligner '%s'" % aligner)
        
        return aligner
    
    # fixme: usage in progress, ill-formed
    def usage(self, context):
        if self.aligner=='bowtie':
            if self.paired_end():

                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
bowtie ${ewbt} -1 %s -2 %s ${args} | perl -lane 'print unless($$F[1] == 4)' > ${ID}.%s_BAD.${format}
                ''' % (context.inputs[self.name][0], context.inputs[self.name][1], self.name)


            else:
                usage='''
export BOWTIE_INDEXES=${config['rnaseq']['bowtie_indexes']}
bowtie ${ewbt} ${args} %s | perl -lane 'print unless($$F[1] == 4)' > ${ID}.%s_BAD.${format}
                ''' % (context.inputs[self.name][0], self.name)
                restore_indent=True

                

        elif self.aligner=='blat':
            pass
        else:
            raise ConfigError("Unknown alignment program '%s'" % self.aligner)


        return usage


    def outputs(self):
        output='${ID}.%s_BAD.${format}' % self.name
        return [output]
    
