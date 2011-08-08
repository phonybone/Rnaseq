from Rnaseq import *

class samtool_copy(Step):
    def usage(self, context):
        usage='''
$${programs}/samtools view -h $${ID}.sorted.bam > $${ID}.sorted.sam
'''
        return usage

    def output_list(self, *args):
        return ['${ID}.sorted.sam']
        
