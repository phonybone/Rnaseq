from Rnaseq import *

class mapsplice2(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='mapsplice2'

    def usage(self,context):
        usage='''
grep chr ${ID}.mapsplice/alignments.sam | perl -lane '$$F[1] == 16 ? print "$$_\tXS:A:-" : print "$$_\tXS:A:+"' > ${ID}.mapsplice.sam
rm -rf ${ID}.mapsplice
'''
        return usage

    def output_list(self, *args):
        return ['${ID}.mapsplice.sam']
    
    
