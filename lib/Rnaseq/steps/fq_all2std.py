from Rnaseq import *
class fq_all2std(Step):
    cmds=['scarf2std', 'fqint2std', 'sol2std', 'fasta', 'fastq', 'fa2std', 'fq2fa', 'solexa2fasta', 'solexa2fastq']

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        # fixme: catch AttributeErrors for these:
        assert self.cmd in self.cmds
        assert self.format != None


    def usage(self, context):
        usage='''
perl ${programs}/fq_all2std.py ${cmd} ${inputs[0]} ${ID}.${format}
        '''
        return usage
    
