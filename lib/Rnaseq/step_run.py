from sqlalchemy import *

class StepRun(object):
    __tablename__='step_run'

    
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)

    @classmethod
    def create_table(self, metadata, engine):
        step_run_table=Table(self.__tablename__, metadata,
                             Column('id', Integer, primary_key=True),
                             Column('step_id', String, ForeignKey('step.id'), nullable=False),
                             Column('pipeline_run_id', String, ForeignKey('step.id'), nullable=False),
                             Column('start_time', Integer),
                             Column('finish_time', Integer),
                             Column('status', String),
                             Column('successful', Boolean))
        metadata.create_all(engine)
        return step_run_table
