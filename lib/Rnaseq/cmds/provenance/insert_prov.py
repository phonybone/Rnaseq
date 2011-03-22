#-*-python-*-
from warn import *
from RnaseqGlobals import RnaseqGlobals
from Rnaseq.command import *

try:
    import sqlite3
except:
    from pysqlite2 import dbapi2 as sqlite3



class InsertProv(Command):
    def description(self):
        return "insert a dataset (path) and authoring script into the database"
    
    def run(self,**args):
        try:
            dbh=args['dbh']
            argv=args['argv']           # assume args=[path, author]
            path=argv[2]                # [0] is script name, [1] is command
            author=argv[3]
            tablename=RnaseqGlobals.conf_value('db','tablename')
            sql="INSERT INTO %s (path, author) VALUES ('%s', '%s')" % (tablename, path, author)
            dbh.execute(sql)
            dbh.commit()
            print "data %s inserted" % path

        except KeyError as e:
            raise MissingArgError(str(e))
        except IndexError as e:
            raise UserError("Missing args in '%s' (insert needs <path> and <author>, in that order)" % " ".join(argv[1:3]))
        #except OperationalError as oe:
        #raise str(oe)
            
#print __file__, "checking in"
