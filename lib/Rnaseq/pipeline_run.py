from RnaseqGlobals import *
from sqlalchemy import *
from sqlalchemy.orm import backref, relationship, mapper
import time
from time_helpers import duration


from step_run import StepRun

class PipelineRun(object):
    __tablename__='pipeline_run'
    time_format="%H:%M:%S %d%b%y"
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    @classmethod
    def create_table(self, metadata, engine):
        pipeline_run_table=Table(self.__tablename__, metadata,
                                 Column('id', Integer, primary_key=True),
                                 Column('pipeline_id', String, ForeignKey('pipeline.id'), nullable=False),
                                 Column('label', String, nullable=False),
                                 Column('working_dir', String),
                                 Column('input_file',  String),
                                 Column('current_step_run_id', Integer),
                                 Column('start_time', Integer),
                                 Column('finish_time', Integer),
                                 Column('status', String),
                                 Column('user',String),
                                 Column('successful', Boolean))
        metadata.create_all(engine)

        sa_properties={'step_runs':relationship(StepRun, backref='pipeline_run', cascade='all, delete, delete-orphan')}
        mapper(PipelineRun, pipeline_run_table, sa_properties)
        return pipeline_run_table


    def __str__(self):
        try:
            if self.start_time==None: raise Exception
            if self.finish_time==None: raise Exception
            dur=duration(self.start_time, self.finish_time, 2)
        except: dur='dur=n/a'
        return "\t".join(str(x) for x in [self.pipeline.name, self.id, self.status, self.successful, self.starttime(), self.finishtime(),
                                          dur])
                                          

    def starttime(self):
        return time.strftime(self.time_format, time.localtime(self.start_time))

    def finishtime(self):
        return time.strftime(self.time_format, time.localtime(self.finish_time))

    def summary(self):
        try:
            session=RnaseqGlobals.get_session()
            last_step=session.query(StepRun).get(self.current_step_run_id)
            last_step_name=last_step.step_name
        except Exception as e:
            last_step_name='n/a'

        try: start_time=time.strftime(self.time_format, time.localtime(self.start_time))
        except: start_time='n/a'

        try: dur=duration(self.start_time, self.finish_time, 2)
        except: dur='n/a'
            
        return "(%d) start time: %s\tduration: %s\tstatus: %s\tsuccessful: %s\tlast step: %s" % \
               (self.id, start_time, dur, self.status, ('yes' if self.successful else 'no'), last_step_name)

    # produce a full report of the pipeline run
    # fixme: should include which readset was used
    def report(self):
        try: dur=duration(self.start_time, self.finish_time, 2)
        except: dur='n/a'
        report="pipeline: '%s' (pr_id=%d)\tstatus: %s\tsuccess: %s\ttotal duration: %s\n" % \
                (self.pipeline.name, self.id, self.status, ('yes' if self.successful else 'no'), dur)
        report+="        input file: %s\n" % self.input_file
        report+="        Steps:\n"
        for step_run in self.step_runs:
            report+="\t%s\n\n" % step_run.report()
        return report

#print __file__,"checking in"
