#-*-python-*-

import yaml, socket, os, glob
from dict_like import dict_like
from templated import templated
from sqlalchemy import *
from table_base import TableBase

class Readset(templated, TableBase):
    def __init__(self,*args,**kwargs):
        templated.__init__(self,*args,**kwargs)
        self.suffix='syml'
        self.type='readset'
    
    ########################################################################
        
    __tablename__='readset'

    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    reads_file=Column(String)
    org=Column(String)
    readlen=Column(Integer)
    working_dir=Column(String)

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

    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

    def path_iterator(self):
        return glob.glob(self['reads_file'])

