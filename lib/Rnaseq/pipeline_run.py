import time
from Rnaseq.pipeline import Pipeline
from table_base import TableBase
from sqlalchemy import *
from sqlalchemy.orm import backref, relation

#class PipelineRun(TableBase):
class PipelineRun(object):
    __tablename__='pipeline_run'
        
    def __init__(self,pipeline):
        self.pipeline=pipeline
        try:
            self.pipeline_id=pipeline.id
        except AttributeError:
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
