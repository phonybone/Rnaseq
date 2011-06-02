from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals

class align(Step):
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
            self.usage='%(exe)s %(ewbt)s %(args)s --un %(unmapped)s %(input)s'
            self.exe='bowtie'
            self.sh_template='bowtie.tmpl'
            self.args='--quiet -p 4 -S --sam-nohead -k 1 -v 2 -q'
            self.align_suffix='fq'
        elif aligner=='blat':
            self.usage='%(exe)s %(blat_index)s %(input)s %(args)s %(psl)s'
            self.exe='blat'
            self.sh_template='blat.tmpl'
            self.args='-fastMap -q=DNA -t=DNA'
            self.align_suffix='fa'
        else:
            raise UserError("unknown aligner '%s'" % aligner)
        
        try: setattr(self.pipeline,'align_suffix',self.align_suffix)
        except: pass
        return aligner
    
