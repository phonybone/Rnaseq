from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from time_helpers import duration
from file_output import *

class StepRun(object):
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)


    def __str__(self):
        try: d=duration(self.start_time, self.finish_time, 2)
        except: d='start=%s, finish=%s' % (self.start_time, self.finish_time)
        return "\t"+" ".join("%-20s"%x for x in [self.step_name, self.status, self.successful, d, self.id])

    ########################################################################
            
    __tablename__='step_run'

    @classmethod
    def create_table(self, metadata, engine):
        step_run_table=Table(self.__tablename__, metadata,
                             Column('id',              Integer, primary_key=True),
                             Column('step_name',       String,  nullable=False),
                             Column('pipeline_run_id', Integer, ForeignKey('pipeline_run.id'), nullable=False),
                             Column('cmd',             String),
                             Column('start_time',      Integer),
                             Column('finish_time',     Integer),
                             Column('status',          String),
                             Column('successful',      Boolean))
        metadata.create_all(engine)
        sa_properties={'file_outputs':relationship(FileOutput, backref='step_run', cascade='all, delete, delete-orphan')}
        mapper(StepRun, step_run_table, sa_properties)
        return step_run_table

    def report(self):
        try: id=self.id
        except: id=None
        
        try: dur=duration(self.start_time, self.finish_time, 2)
        except: dur='n/a'
        lines=[]
        lines.append("%-25s status: %s\tsuccess: %s\tduration: %s\tid: %s" % (self.step_name, self.status, ('passed' if self.successful else 'failed'), dur, id))
        for output in self.file_outputs:
            lines.append("%soutput: %s" % (' '*34, output.report()))
        return "\n".join(lines)
