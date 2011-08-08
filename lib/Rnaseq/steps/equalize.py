from Rnaseq import *

class equalize(Step):

    def usage(self, context):
        inputs=' '.join(context.inputs[self.name])
        inputs=re.sub('\$\{', '$${', inputs)

        outputs=' '.join(self.output_list())
        outputs=re.sub('\$\{', '$${', outputs)
        


        usage='''
perl $${programs}/removeBadReads.pl -v -paired %(inputs)s - %(outputs)s
''' % {'inputs':inputs, 'outputs':outputs}
        return usage


    def output_list(self,*args):
        if self.paired_end():
            return ['${ID}_GOOD_1.${format}', '${ID}_GOOD_2.${format}']
        else:
            return ['${ID}_GOOD.${format}']
    
