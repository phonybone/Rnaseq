#-*-python-*-
from warn import *

class ProvCmd:
    def run(self):
        raise ProgrammerGoof(str(self.__class__)+".run not implemented")
    

