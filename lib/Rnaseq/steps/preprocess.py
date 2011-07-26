from Rnaseq import *

class preprocess(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='preprocess'
        self.description='Perform basic operations including (barcoding, masking, removal) on a readset'
        self.usage='%(interpreter)s %(exe)s %(args)s -i %(input)s -o %(output)s'
        self.interpreter='perl'
        self.exe='preprocessReads.pl'

    def usage(self, context):
        script='''
perl ${programs}/preprocessReads.pl ${args} -i ${inputs[0]} -o ${ID}.pre
'''
        return script

    def output_list(self):
        return '${ID}.pre'
        
