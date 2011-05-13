from Rnaseq import *
class fq_all2std(Step):
    exe='fq_all2std.pl'
    interpreter='perl'
    cmds=['scarf2std', 'fqint2std', 'sol2std', 'fasta', 'fastq', 'fa2std', 'fq2fa', 'solexa2fasta', 'solexa2fastq']
    usage='%(interpreter)s %(exe)s %(args)s %(input)s %(output)s'

print __file__,"checking in"
