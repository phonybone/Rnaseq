from Rnaseq import *

class cuffcompare(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='cuffcompare'
        self.exe='cuffcompare'
        self.usage='%(exe)s %(genome_dir)s/%(genome)s.gtf -s %(genome_dir)s/%(genome)s.fa -o %(output)s %(input)s'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'
