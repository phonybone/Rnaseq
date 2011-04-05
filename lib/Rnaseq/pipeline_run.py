import time
from Rnaseq.pipeline import Pipeline
from table_base import TableBase
from sqlalchemy import *
from sqlalchemy.orm import backref, relation

class PipelineRun(TableBase):
    __tablename__='pipeline_run'
    id=Column(Integer, primary_key=True)
    pipeline_id=Column(Integer, ForeignKey('pipeline.id'))
    start_time=Column(Integer)
    finish_time=Column(Integer)
    status=Column(String)
    successful=Column(Boolean)
    pipeline=relation(Pipeline,backref=backref(Pipeline.__tablename__, order_by=id))
        
    def __init__(self,pipeline):
        pass

    @classmethod
    def create_table(self, metadata, engine):
        pipeline_run_table=Table(self.__tablename__, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('pipeline_id', String, ForeignKey('pipeline.id'), nullable=False),
                                 Column('start_time', Integer),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)
        return pipeline_run_table
