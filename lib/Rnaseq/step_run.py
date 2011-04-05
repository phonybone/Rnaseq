import time
from Rnaseq.step import Step
from table_base import TableBase
from sqlalchemy import *
from sqlalchemy.orm import backref, relation

class StepRun(TableBase):
    __tablename__='step_run'
    id=Column(Integer, primary_key=True)
    step_id=Column(Integer, ForeignKey('step.id'))
    start_time=Column(Integer)
    finish_time=Column(Integer)
    status=Column(String)
    successful=Column(Boolean)
    step=relation(Step,backref=backref(Step.__tablename__, order_by=id))

    
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)

    @classmethod
    def create_table(self, metadata, engine):
        step_run_table=Table(self.__tablename__, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('step_id', String, ForeignKey('step.id'), nullable=False),
                                 Column('start_time', Integer, nullable=False, default=int(time.time())),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)
        return step_run_table
