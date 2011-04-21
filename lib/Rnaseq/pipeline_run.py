from sqlalchemy import *
from sqlalchemy.orm import backref, relationship, mapper
import time
from time_helpers import duration


from step_run import StepRun

class PipelineRun(object):
    __tablename__='pipeline_run'
    time_format="%d%b%y %H:%M:%S"
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    @classmethod
    def create_table(self, metadata, engine):
        pipeline_run_table=Table(self.__tablename__, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('pipeline_id', String, ForeignKey('pipeline.id'), nullable=False),
                                 Column('current_step_run_id', Integer),
                                 Column('start_time', Integer),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)

        sa_properties={'step_runs':relationship(StepRun, backref='pipeline_run')}
        mapper(PipelineRun, pipeline_run_table, sa_properties)
        return pipeline_run_table


    def __str__(self):
        try:
            if self.start_time==None: raise Exception
            if self.finish_time==None: raise Exception
            dur=duration(self.start_time, self.finish_time)
        except: dur=''
        return "\t".join(str(x) for x in [self.pipeline.name, self.id, self.status, self.successful, self.starttime(), self.finishtime(),
                                          dur])
                                          

    def starttime(self):
        return time.strftime(self.time_format, time.localtime(self.start_time))

    def finishtime(self):
        return time.strftime(self.time_format, time.localtime(self.finish_time))
