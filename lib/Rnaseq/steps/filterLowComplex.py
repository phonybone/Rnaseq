from Rnaseq import *
class filterLowComplex(Step):
    def __init__(self,**kwargs):
        Step.__init__(self,**kwargs)
        self.name='filterLowComplex'
        self.description='Remove sequences with low complexity'
        self.usage='%(interpreter)s %(exe)s %(args)s -i %(input)s -o %(output)s -b %(filtered)s'
        self.interpreter='perl'
        self.exe='filterLowComplex.pl'
