from sqlalchemy import *
from sqlalchemy.orm import backref, relationship, mapper

from step_run import StepRun

class PipelineRun(object):
    __tablename__='pipeline_run'
    sa_properties={'step_runs':relationship(StepRun, backref='pipeline_run')}

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
        mapper(PipelineRun,pipeline_run_table,PipelineRun.sa_properties)
        print "%s table %s created" %(self.__name__,self,__tablename__)
        return pipeline_run_table

'''
    def __str__(self):
        session=RnaseqGlobals.get_session()
        try:
            pipeline_name=session.query(Pipeline).filter_by(id=self.pipeline_id).first().name
        except:
            pipeline_name="<none>"
        try:
            cur_steprun=session.query(StepRun).filter_by(id=self.current_step_run_id).first
'''            
