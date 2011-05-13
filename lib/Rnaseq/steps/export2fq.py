from Rnaseq import *
from Rnaseq.steps.fq_all2std import fq_all2std

class export2fq(fq_all2std):
    cmd='solexa2fastq'
