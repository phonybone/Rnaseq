import time
from Rnaseq.step import Step
from Rnaseq.pipeline_run import PipelineRun
from sqlalchemy import *
from sqlalchemy.orm import backref, relation

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
                                 Column('start_time', Integer, nullable=False, default=int(time.time())),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)
        return step_run_table
