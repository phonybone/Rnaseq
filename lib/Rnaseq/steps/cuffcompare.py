from Rnaseq import *

class cuffcompare(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='cuffcompare'
        self.exe='cuffcompare'
        self.usage='%(exe)s %(genome_dir)s/%(genome)s.gtf -s %(genome_dir)s/%(genome)s.fa -o %(output)s %(input)s'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'

    def usage(self, context):
        usage='''
genome_dir=${genome_dir}
genome=${genome}
${programs}/cuffcompare $${genome_dir}/$${genome}.gtf -s $${genome_dir}/$${genome}.fa -o ${ID}.cuffcompare ${inputs[0]}
        '''
        return usage

    def output_list(self):
        return ['${ID}.cuffcompare']
