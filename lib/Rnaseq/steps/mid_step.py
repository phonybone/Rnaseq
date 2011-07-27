from Rnaseq import *
class mid_step(Step):

    def __init__(self, **kwargs):
        Step.__init__(self,**kwargs)
        self.is_prov_step=True
        
    def usage(self, context):
        if RnaseqGlobals.conf_value('debug'): self.debug='-d'
        else: self.debug=''

        usage='''
# check success of step ${stepname}:
exit_on_failure $$? ${pipeline_run_id} ${step_run_id} ${next_step_run_id} ${debug}
        '''
        return usage

    def output_list(self):
        return []
    
