from Rnaseq import *

class cufflinks(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        #self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        #self.genome='hs37.61'
        self.ensembl='/proj/hoodlab/share/programs/Ensembl'
        
    def usage(self,context):
        try: threads='-p %d' % self.threads
        except AttributeError: threads=''
        
        usage='''
ensembl=${ensembl}
mask_file=$${ensembl}/Homo_sapiens.GRCh37.62.PSEUDO.corr.gtf
gtf_guide=$${ensembl}/Homo_sapiens.GRCh37.62.corr.gtf
bias_correct=$${ensembl}/hg19_exp.fa

$${programs}/cufflinks -o $${ID}.cufflinks %(threads)s --frag-bias-correct $${bias_correct} -u -g $${gtf_guide} -M $${mask_file} $${ID}.sorted.bam
        ''' % {'threads': threads}

        return usage

    def output_list(self):
        return ['${ID}.cufflinks/genes.expr',  '${ID}.cufflinks/genes.fpkm_tracking',  '${ID}.cufflinks/isoforms.fpkm_tracking',  '${ID}.cufflinks/transcripts.expr',  '${ID}.cufflinks/transcripts.gtf']
    
