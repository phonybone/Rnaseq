from Rnaseq import *
class pipeline_end(Step):

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.is_prov_step=True


    def usage(self, context):
        if RnaseqGlobals.conf_value('debug'): self.debug='-d'
        else: self.debug=''

        usage='''
python ${root_dir}/bin/provenance pipeline_end ${pipelinerun_id} ${debug}
'''
        return usage

    def output_list(self, *args):
        return []
