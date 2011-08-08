from Rnaseq import *

class bowtie2bam(Step):
    def usage(self, context):
        usage='''
$${programs}/samtools view -b -h -S -u $${ID}.bowtie.sam | $${programs}/samtools sort - $${ID}.sorted
'''
        return usage

    def output_list(self,*args):
        return ['${ID}.sorted.bam']
        
