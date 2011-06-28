from Rnaseq import *
class filterQuality(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterQuality'
        self.description='Remove sequences with low quality scores'
        self.args='-v'

    def usage(self, context):
        if self.readset.paired_reads:

            usage='''
perl $${programs}/filterQuality.pl ${args} -f ${format} -i %s -o ${ID}.qual_OK_1.${format} -b ${ID}.qual_BAD_1.${format}
perl $${programs}/filterQuality.pl ${args} -f ${format} -i %s -o ${ID}.qual_OK_2.${format} -b ${ID}.qual_BAD_2.${format}
            ''' % (context.inputs[0], context.inputs[1])

            context.outputs=["%s.qual_OK_1.%s" % (context.ID, context.format),
                            "%s.qual_OK_2.%s" % (context.ID, context.format)]
            context.creates=["%s.qual_BAD_1.%s" % (context.ID, context.format)]
        else:

            usage='''
perl $${programs}/filterQuality.pl ${args} -f $${format} -i %s -o ${ID}.qual_OK.${format} -b ${ID}.qual_BAD.${format}
            ''' % context.inputs[0]
            
            context.outputs=["%s.qual_OK.%s" % (context.ID, context.format)]
            context.creates=["%s.qual_BAD.%s" % (context.ID, context.format)]

        return (usage, context)

    def creates(self):
        pass
    
