from sqlalchemy import *
from sqlalchemy.orm import backref, relation

#class PipelineRun(TableBase):
class PipelineRun(object):
    __tablename__='pipeline_run'
        
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    @classmethod
    def create_table(self, metadata, engine):
        pipeline_run_table=Table(self.__tablename__, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('pipeline_id', String, ForeignKey('pipeline.id'), nullable=False),
                                 Column('current_step_run_id', Integer, ForeignKey('step_run.id')),
                                 Column('start_time', Integer),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)
        return pipeline_run_table
