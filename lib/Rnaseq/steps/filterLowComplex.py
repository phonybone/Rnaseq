from Rnaseq import *
class filterLowComplex(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterLowComplex'
        self.description='Remove sequences with low complexity'
        self.args='-v'

    # needs a better way to know what the input is (not harded, as is; don't want this to be order dependent
    def usage(self,context):
        if self.paired_end():

            usage='''
perl $${programs}/filterLowComplex.pl ${args} -f ${format} -i %s -o ${ID}.complex_OK_1.${format} -b ${ID}.complex_BAD_1.${format}
perl $${programs}/filterLowComplex.pl ${args} -f ${format} -i %s -o ${ID}.complex_OK_2.${format} -b ${ID}.complex_BAD_2.${format}
            ''' % (context.inputs[self.name][0], context.inputs[self.name][1])
            
        else:

            usage='''
perl $${programs}/filterLowComplex.pl ${args} -f $${format} -i %s -o ${ID}.complex_OK.${format} -b ${ID}.complex_BAD.${format}
            ''' % context.inputs[self.name][0]

        return usage


    def outputs(self):
        if self.paired_end():
            return ['${ID}.complex_BAD_1.${format}','${ID}.complex_BAD_1.${format}']
        else:
            return ['${ID}.complex_BAD.${format}']


    def cleanup_script(self):
        pass
    
    
