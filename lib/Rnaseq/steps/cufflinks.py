from Rnaseq import *

class cufflinks(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        #self.name='cufflinks'
        #self.sh_template='cufflinks.tmpl'
        #self.usage="%(exe)s -q -p ${qsub['nprocs']}  -o %(output)s %(input)s"
        #self.exe='cufflinks'
        self.genome_dir='/proj/hoodlab/share/programs/Ensembl'
        self.genome='hs37.61'
        
    def usage(self,context):
        try: threads='-p %d' % self.threads
        except AttributeError: threads=''
        
        usage='''
ensembl=${endembl}
mask_file=$${ensembl}/Homo_sapiens.GRCh37.62.PSEUDO.corr.gtf
gtf_guide=$${ensembl}/Homo_sapiens.GRCh37.62.corr.gtf
bias_correct=$${ensembl}/hg19_exp.fa

${programs}/cufflinks -o ${ID}.cufflinks %(threads)s --frag-bias-correct $${bias_correct} -u -g $${gtf_guide} -M $${mask_file} ${ID}.sorted.bam
        ''' % {'threads': threads}

        return usage

    def outputs(self):
        return ['${ID}.cufflinks/genes.expr',  '${ID}.cufflinks/genes.fpkm_tracking',  '${ID}.cufflinks/isoforms.fpkm_tracking',  '${ID}.cufflinks/transcripts.expr',  '${ID}.cufflinks/transcripts.gtf']
    
