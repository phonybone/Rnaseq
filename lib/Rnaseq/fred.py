from templated import *
from sqlalchemy import *

class fred(templated):
    def __init__(self,*args,**kwargs):
        templated.__init__(self,*args,**kwargs)

    __tablename__='fred'
    
    @classmethod
    def create_table(self, metadata, engine):
        fred_table=Table(self.__tablename__, metadata,
                         Column('id',Integer, primary_key=True),
                         Column('name',String),
                         Column('description', String),
                         )
        metadata.create_all(engine)
        return fred_table
    
