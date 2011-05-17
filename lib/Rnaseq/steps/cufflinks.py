from Rnaseq import *

class cufflinks(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='cufflinks'
        self.sh_template='cufflinks.tmpl'
        self.usage="%(exe)s -q -p ${qsub['nprocs']}  -o %(output)s %(input)s"
        self.exe='cufflinks'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'
        
