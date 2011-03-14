#-*-python-*-
from warn import *

class Command:
    def run(self):
        raise ProgrammerGoof(str(self.__class__)+".run not implemented (abstract method)")
    

