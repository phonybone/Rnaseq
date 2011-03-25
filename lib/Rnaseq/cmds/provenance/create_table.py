#-*-python-*-
from warn import *
from Rnaseq.command import *
from sqlite3 import OperationalError
from RnaseqGlobals import RnaseqGlobals

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

        method_name="create_%s" % tablename
        try:
            method=getattr(self,method_name)
        except AttributeError as ae:
            raise UserError("Don't know how to create table %s" % tablename)

        method(*argv,**args)


    def create_provenance(self, *argv, **args):
        try:
            dbh=args['dbh']
            tablename=argv[0][2]
            if RnaseqGlobals.value.force:
                dbh.execute("DROP TABLE IF EXISTS %s" % tablename)
        except KeyError as e:
            raise MissingArgError(e)
        except IndexError as ie:
            raise MissingArgError(ie)

        try:
            sql='''
CREATE TABLE %s (
id INTEGER PRIMARY KEY AUTOINCREMENT,
path VARCHAR[255] NOT NULL,
author VARCHAR[255] NOT NULL
);''' % tablename
        
            dbh.execute(sql)
            print "table %s created" % tablename
        except OperationalError as oe:  # OperationalError a sql thing
            raise ProgrammerGoof("%s in %s" % (oe,sql))


        
    def create_pipeline(self,*argv,**args):
        try:
            dbh=args['dbh']
            tablename=argv[0][2]
            if RnaseqGlobals.conf_value('force'):
                dbh.execute("DROP TABLE IF EXISTS %s" % tablename)
        except KeyError as e:
            raise MissingArgError(e)
        except IndexError as ie:
            raise MissingArgError(ie)

        sql='''
CREATE TABLE %s (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR[255] NOT NULL,
status VARCHAR[255] NOT NULL,
success INTEGER NOT NULL DEFAULT 0)
''' % tablename

        try:
            dbh.execute(sql)
            print "table %s created" % tablename
        except OperationalError as oe:  # OperationalError a sql thing
            raise ProgrammerGoof("%s in %s" % (oe,sql))

