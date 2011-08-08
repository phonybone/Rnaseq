from Rnaseq import *

class mapsplice(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='mapsplice'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'

    def usage(self, context):
        usage='''
genome_dir=${genome_dir}
genome=${genome}
python $${programs}/mapsplice_segments.py -c $${genome_dir}/$${genome}.fa -B $${blat_index}/$${genome} -t $${genome_dir}/$${genome}.pseudo.gtf -w ${pipeline.readset['readlen']} -L 25 -Q $${format} -X 6  -u ${inputs[0]} -o $${ID}/mapsplice
'''
        return usage

    def output_list(self, *args):
        return ['${working_dir}/${ID}.mapsplice/alignments.sam','${working_dir}/${ID}.mapsplice/best_junction.bed']
