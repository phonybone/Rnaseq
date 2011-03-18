#-*-python-*-
from warn import *
from Rnaseq.command import *
from sqlite3 import OperationalError
import optparse, os, time

# usage: provenance ls [glob]

class ListFiles(Command):
    def description(self):
        return "list the contents of the provenance table (filter with fileglob)"

    def run(self, **args):
        try:
            dbh=args['dbh']
            argv=args['argv']           # assume args=[path, author]
            tablename=optparse.options.conf['db']['tablename']
            sql="SELECT * FROM %s" % tablename
            if len(argv) > 2:
                glob=argv[2]    # [0] is script name, [1] is command
                re.sub('\*','\%',glob)
                sql+=" WHERE path LIKE '%s'" % glob

            cursor=dbh.cursor()
            cursor.execute(sql)
            rows=cursor.fetchall()
            for row in rows:
                (path,author)=row[1:3]
                try: 
                    mtime=time.strftime('%b %d %Y %H:%M:%S', time.localtime(int(os.stat(path).st_mtime)))
                except OSError:
                    mtime='file not found'
                print "%-50s\t%20s\t%s" % (path, mtime, author)

        except KeyError as e:
            raise MissingArgError(str(e))
        except IndexError as e:
            raise UserError("Missing args in '%s'" % " ".join(argv[1:3]))
        #except OperationalError as oe:
        #raise str(oe)

#print __file__, "checking in"
