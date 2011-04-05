#-*-python-*-
import os

import Rnaseq
from Rnaseq import *
from Rnaseq.command import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from sqlite3 import OperationalError
from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker

class CreateTable(Command):
    def description(self):
        return "create a provenance database table (administrator use only)"
    
    def usage(self):
        return "usage: create_table <tablename> [--force]"

    def run(self,*argv,**args):
        try:
            tablename=argv[0][2]
        except IndexError:
            raise UserError(self.usage())


    classes=[Pipeline, PipelineRun, Step, StepRun]

    def run(self,*argv,**args):
        db_name=os.path.join(RnaseqGlobals.conf_value('rnaseq','root_dir'), 'db', RnaseqGlobals.conf_value('db','db_name'))
        engine=create_engine('sqlite:///%s' % db_name, echo=False)
        print "connected to %s" % db_name
        metadata=MetaData()
        Session=sessionmaker(bind=engine)
        session=Session()

        for klass in self.classes:

            # Drop the table first.  Don't try to use Table.drop(), it's a pain if the table doesn't already exist.
            #engine.execute("DROP TABLE IF EXISTS %s" % tablename)
        
            try: ct=getattr(klass,'create_table')
            except AttributeError as ae:
                raise UserError("%s doesn't define 'create_table'" % klass.__name__)
            
            ct(metadata, engine)
            print "%s created" % klass.__tablename__
        
