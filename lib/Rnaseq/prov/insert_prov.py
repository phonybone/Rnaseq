#-*-python-*-
from warn import *
from Rnaseq.prov.prov_cmd import *
from sqlite3 import OperationalError
import optparse

class InsertProv(ProvCmd):
    def run(self,**args):
        try:
            dbh=args['dbh']
            argv=args['argv']           # assume args=[path, author]
            path=argv[2]                # [0] is script name, [1] is command
            author=argv[3]
            tablename=optparse.options.conf['db']['tablename']
            sql="INSERT INTO %s (path, author) VALUES ('%s', '%s')" % (tablename, path, author)
            dbh.execute(sql)
            dbh.commit()
            
        except KeyError as e:
            die(MissingArgError(str(e)))
        except IndexError as e:
            die(UserError("Missing args in '%s' (insert needs <path> and <author>, in that order)" % " ".join(argv[1:3])))
        except OperationalError as oe:
            die(str(oe))
            
