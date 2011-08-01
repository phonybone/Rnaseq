#-*-python-*-
from warn import *

class Command(object):
    def __init__(self):
        self.readsets=[]
        self.pipelines={}               # k=readset, as above; v=pipeline for that readset
        
    def run(self):
        raise ProgrammerGoof(str(self.__class__)+".run not implemented (abstract method)")

    def description(self):
        return "no description provided for %s" % self.__class__

    def usage(self):
        return "no usage provided for %s" % self.__class__

