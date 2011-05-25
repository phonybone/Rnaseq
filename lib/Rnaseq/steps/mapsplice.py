from Rnaseq import *

class mapsplice(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='mapsplice'
        self.usage="%(interpreter)s %(exe)s -c %(genome_dir)s/%(genome)s.fa -B ${blat_index}/%(genome)s -t %(genome_dir)s/%(genome)s.pseudo.gtf -w ${pipeline.readset['readlen']} -L 25 -Q ${pipeline.align_suffix} -X ${qsub['nprocs']}  -u %(input)s -o %(output)s"
        self.exe='mapsplice_segments.py'
        self.interpreter='python'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'
