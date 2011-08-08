from Rnaseq import *
class fq_all2std(Step):
    cmds=['scarf2std', 'fqint2std', 'sol2std', 'fasta', 'fastq', 'fa2std', 'fq2fa', 'solexa2fasta', 'solexa2fastq']

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        # fixme: catch AttributeErrors for these:
        assert self.cmd in self.cmds
        assert self.format != None



    def usage(self, context):
        #print "fq_all: context.inputs is %s" % context.inputs

        usage="\nformat=%s\n" % self.format
        if (self.paired_end()):
            usage+='''
perl $${programs}/fq_all2std.py solexa2fq ${inputs[0]} ${inputs[1]} $${ID}_1.$${format}
            ''' 
        else:
            usage+='''
perl $${programs}/fq_all2std.py ${cmd} ${inputs[0]} $${ID}.$${format}
            ''' 


        return usage


    def output_list(self):
        if self.paired_end():
            return ['${ID}_1.${format}','${ID}_2.${format}']
        else:
            return ['${ID}.${format}']
    
