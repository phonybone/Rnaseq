from Rnaseq import *

class cuffcompare(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='cuffcompare'
        self.genome='hs37.61'

    def usage(self, context):
        usage='''
ensembl_dir=${config['rnaseq']['ensembl_dir']}
$${programs}/cuffcompare $${ensembl_dir}/${genome}.gtf -s $${ensembl_dir}/${genome}.fa -o ${ID}.cuffcompare ${inputs[0]}
        '''
        return usage

    def output_list(self,*args):
        return ['${ID}.cuffcompare']
