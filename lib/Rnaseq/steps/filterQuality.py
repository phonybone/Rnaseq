from Rnaseq import *
class filterQuality(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterQuality'
        self.description='Remove sequences with low quality scores'
        self.args='-v'

    def usage(self, context):
        if self.paired_end():
            usage='''
perl $${programs}/filterQuality.pl ${args} -f $${format} -i ${inputs[0]} -o /dev/null -b $${ID}.qual_BAD_1.$${format}
perl $${programs}/filterQuality.pl ${args} -f $${format} -i ${inputs[1]} -o /dev/null -b $${ID}.qual_BAD_2.$${format}
            ''' 

        else:
            usage='''
perl $${programs}/filterQuality.pl ${args} -f $${format} -i ${inputs[0]} -o ${ID}.qual_OK.$${format} -b ${ID}.qual_BAD.$${format}
            '''
            

        return usage

    def output_list(self,*args):
        if self.paired_end():
            return ['${ID}.qual_BAD_1.${format}','${ID}.qual_BAD_1.${format}']
        else:
            return ['${ID}.qual_BAD.${format}']
    
