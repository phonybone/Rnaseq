from Rnaseq import *
class fq_all2std(Step):
    cmds=['scarf2std', 'fqint2std', 'sol2std', 'fasta', 'fastq', 'fa2std', 'fq2fa', 'solexa2fasta', 'solexa2fastq']

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.exe='fq_all2std.pl'
        self.interpreter='perl'
        self.usage='%(interpreter)s %(exe)s %(args)s %(input)s %(output)s'

    def usage(self):
        usage='''
perl programs/fq_all2std.py ${cmd} ${input} ${output}
        '''
        return usage
    
