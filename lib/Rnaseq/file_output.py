from sqlalchemy import *
from sqlalchemy.orm import mapper
import time
from evoque_helpers import evoque_template


class FileOutput(object):
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)


    __tablename__='file_output'
    time_format="%H:%M:%S %d%b%y"

    @classmethod
    def create_table(self, metadata, engine):
        file_output_table=Table(self.__tablename__, metadata,
                                Column('id',              Integer, primary_key=True),
                                Column('path',            String,  nullable=False),
                                Column('create_time',     Integer),
                                Column('steprun_id',      Integer, ForeignKey('step_run.id'),         nullable=False))
        metadata.create_all(engine)
        mapper(FileOutput, file_output_table)
        return file_output_table

    def report(self):
        return "%s\t%s" % (self.path, time.strftime(self.time_format, time.localtime(self.create_time)))


