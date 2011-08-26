from Rnaseq import *

class equalize(Step):

    def usage(self, context):
        inputs=context.inputs['equalize']

        filtered=[x for x in inputs if re.search('BAD',x)]
        filtered=' '.join(filtered)

        all_reads=[x for x in inputs if x not in filtered]
        all_reads=' '.join(all_reads)

        paired_flag='-paired' if self.paired_end() else ''

        usage='''
perl $${programs}/removeBadReads.pl -v %(paired_flag)s %(filtered)s - %(all_reads)s
''' % {'filtered':filtered, 'all_reads':all_reads, 'paired_flag':paired_flag}
        return usage


    def output_list(self,*args):
        if self.paired_end():
            return ['${ID}_1.GOOD.${format}', '${ID}_2.GOOD.${format}']
        else:
            return ['${ID}_GOOD.${format}']
    
