from Rnaseq import *
class filterQuality(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterQuality'
        self.description='Remove sequences with low quality scores'
        self.usage='%(interpreter)s %(exe)s %(args)s -i %(input)s -o %(output)s -b %(filtered)s'
        self.interpreter='perl'
        self.exe='filterQuality.pl'
