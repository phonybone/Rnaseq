from Rnaseq import *
class filterLowComplex(Step):
    name='filterLowComplex'
    description='Remove sequences with low complexity'
    usage='%(interpreter)s %(exe)s %(args)s -i %(input)s -o %(output)s -b %(filtered)s'
    interpreter='perl'
    exe='filterLowComplex.pl'
