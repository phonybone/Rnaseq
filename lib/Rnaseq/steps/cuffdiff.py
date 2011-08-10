from Rnaseq import *

class cuffdiff(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)

    def usage(self,context):
        if hasattr(self, 'include_cuffcompare'):
            cuffcompare='$${programs}/cuffcompare -s $${genome_seq} $${annotation} $${annotation}'
        else:
            cuffcompare=''
            
        usage='''
annotation=${annotation}
genome_seq=${genome_seq}
%(cuffcompare)s

$${programs}/cuffdiff -o cuffdiff --num_threads 6 --labels %(labels)s ${inputs}

        '''
        return usage

    def output_list(self,*args):
        return ['']
    
