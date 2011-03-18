#-*-python-*-
from warn import *
from Rnaseq.prov.prov_cmd import *
from sqlite3 import OperationalError
import optparse

class CreateTable(ProvCmd):
    def run(self, **args):
        tablename=optparse.options.conf['db']['tablename']
        try:
            dbh=args['dbh']
            if optparse.options.force:
                dbh.execute("DROP TABLE IF EXISTS %s" % tablename)

            sql='''
CREATE TABLE %s (
id INTEGER PRIMARY KEY AUTOINCREMENT,
path VARCHAR[255] NOT NULL,
author VARCHAR[255] NOT NULL
);''' % tablename
        
            dbh.execute(sql)
            print "table %s created" % tablename
        except KeyError as e:
            raise MissingArgError('dbh')
        except OperationalError as oe:  # OperationalError a sql thing
            warn(str(oe) + " and --force not supplied")
        
    

