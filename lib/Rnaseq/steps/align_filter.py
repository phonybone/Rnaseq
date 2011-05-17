from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals

class align_filter(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

        aligner=RnaseqGlobals.conf_value('rnaseq','aligner')
        if aligner=='bowtie':
            self.usage='%(exe)s %(ewbt)s %(args)s --un %(output)s %(input)s'
            self.exe='bowtie'
            self.sh_template='bowtie_filter.tmpl'
            self.args='--quiet -p 4 -S --sam-nohead -k 1 -v 2 -q'
            self.align_suffix='fq'
        elif aligner=='blat':
            self.usage='%(exe)s %(blat_index)s %(input)s %(args)s %(psl)s'
            self.exe='blat'
            self.sh_template='blat_filter.tmpl'
            self.args='-fastMap -q=DNA -t=DNA'
            self.align_suffix='fa'
        else:
            raise UserError("unknown aligner '%s'" % aligner)
        

