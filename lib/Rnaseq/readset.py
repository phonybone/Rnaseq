#-*-python-*-

import yaml, socket, os, glob
from sqlalchemy import *
from warn import *

#class Readset(templated, TableBase):
class Readset(dict):
    def __init__(self,*args,**kwargs):
        self.suffix='syml'
        self.type='readset'
        for k,v in kwargs.items():
            setattr(self,k,v)
        
    ########################################################################
        
    __tablename__='readset'

    @classmethod
    def create_table(self, metadata, engine):
        readset_table=Table(self.__tablename__, metadata,
                            Column('id',Integer, primary_key=True),
                            Column('name',String,nullable=False),
                            Column('reads_file', String),
                            Column('org', String),
                            Column('readlen', Integer),
                            Column('working_dir', String),
                            useexisting=True,
                         )
        metadata.create_all(engine)
        return readset_table
        
    ########################################################################

    def load(self):
        try:
            f=open(self.filename)
            yml=yaml.load(f)
            f.close()
        except IOError as ioe:
            raise UserError(str(ioe))
        except AttributeError as ae:
            raise ProgrammerGoof(ae)
        self.update(yml)
        for k,v in yml.items():
            setattr(self,k,v)
        return self

    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

    def path_iterator(self):
        try: return glob.glob(self['reads_files'])
        except KeyError: return glob.glob(self['reads_file']) # danger! will get overwritten!

