from Rnaseq import *
class filterLowComplex(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterLowComplex'
        self.description='Remove sequences with low complexity'

    # needs a better way to know what the input is (not harded, as is; don't want this to be order dependent
    def usage(self,context):
        if self.readset.paired_reads:

            usage='''
perl $${programs}/filterLowComplex.pl ${args} -f ${format} -i ${context.inputs[0] -o ${ID}.complex_OK_1.${format} -b ${ID}.complex_BAD_1.${format}
perl $${programs}/filterLowComplex.pl ${args} -f ${format} -i ${context.inputs[1] -o ${ID}.complex_OK_2.${format} -b ${ID}.complex_BAD_2.${format}
            '''
            
            context.outputs=["%s.complex_OK_1.%s" % (context.ID, context.format),
                            "%s.complex_OK_2.%s" % (context.ID, context.format)]
            context.creates=["%s.complex_BAD_1.%s" % (context.ID, context.format)]
        else:

            usage='''
perl $${programs}/filterLowComplex.pl ${args} -f $${format} -i ${ID}.${format} -o ${ID}.complex_OK.${format} -b ${ID}.complex_BAD.${format}
            ''' % context.inputs[0]

            context.outputs=["%s.complex_OK.%s" % (context.ID, context.format)]
            context.creates=["%s.complex_BAD.%s" % (context.ID, context.format)]

        return (usage, context)

    def creates(self):
        pass

    def cleanup_script(self):
        pass
    
    
