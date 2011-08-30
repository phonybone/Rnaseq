from Rnaseq import *

class cufflinks(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.genome='hs37.61'
        
    def usage(self,context):
        try: threads='-p %d' % self.threads
        except AttributeError: threads=''
        self.ensembl_dir=RnaseqGlobals.conf_value('ensembl_dir')
        
        usage='''
ensembl_dir=${ensembl_dir}
mask_file=$${ensembl_dir}/Homo_sapiens.GRCh37.62.PSEUDO.corr.gtf
gtf_guide=$${ensembl_dir}/Homo_sapiens.GRCh37.62.corr.gtf
bias_correct=$${ensembl_dir}/${genome}

$${programs}/cufflinks -o $${ID}.cufflinks %(threads)s --frag-bias-correct $${bias_correct} -u -g $${gtf_guide} -M $${mask_file} $${ID}.sorted.bam
        ''' % {'threads': threads}

        return usage

    def output_list(self,*args):
        return ['${ID}.cufflinks/genes.expr',  '${ID}.cufflinks/genes.fpkm_tracking',  '${ID}.cufflinks/isoforms.fpkm_tracking',  '${ID}.cufflinks/transcripts.expr',  '${ID}.cufflinks/transcripts.gtf']
    
