from Rnaseq import *

class equalize(Step):

    def usage(self, context):
        inputs=context.inputs['equalize']
        inputs=' '.join(context.inputs['equalize'])
        outputs=' '.join(self.output_list())
        paired_flag='-paired' if self.paired_end() else ''

        usage='''
perl $${programs}/removeBadReads.pl -v %(paired_flag)s %(inputs)s - %(outputs)s
''' % {'inputs':inputs, 'outputs':outputs, 'paired_flag':paired_flag}
        return usage


    # bug: "GOOD" not mentioned anywhere above; rather, usage() above is taking as outputs any input
    # not containing the string "BAD" (seems fragile, tstl).
    # Basic problem is that we can't access the input_list to determine the output list
    def output_list(self,*args):
        if self.paired_end():
            l=['${ID}_1.GOOD.${format}', '${ID}_2.GOOD.${format}']
        else:
            l=['${ID}_GOOD.${format}']
        return l
    
