import re, os
from dict_like import dict_like
try:
    import sqlite3
except:
    from pysqlite2 import dbapi2 as sqlite3
from RnaseqGlobals import RnaseqGlobals
from warn import *

class SimpleOrm(dict_like):
    connections={}

    def __init__(self,**args):
        dict_like.__init__(self,**args)
        try:
            self.db_file=args['db_file']
        except KeyError:
            a=RnaseqGlobals.conf_value('rnaseq', 'root_dir')
            b=RnaseqGlobals.conf_value('db','db_name')
            if (a==None or b==None):
                raise ProgrammerGoof("RnaseqGlobals not initialized")
            self.db_file=os.path.join(a,b)

        self.connect()                  # should this really be called in the constructor?
        self.cursor=self.dbh.cursor()
        assert(self.columns)

    # connect to the database, and cache the connection:
    def connect(self):
        try:
            connection=self.connections[self.db_file]
        except KeyError:
            connection=sqlite3.connect(self.db_file)
            self.connections[self.db_file]=connection
        self.dbh=connection
        return connection

    def execute(self,sql,*args):
        t=tuple(args)
        try:
            #print "executing something like %s" % sql
            self.cursor.execute(sql,t)
            self.dbh.commit()
        except sqlite3.OperationalError as oe:
            print "sql error in '%s'" % sql
            raise oe

    def insert(self):
        sql="INSERT INTO %s (id, %s) VALUES (null, %s)" % (self.tablename(), self.fields_str(), self.values_str())
        #print "insert: sql is %s" % sql
        try:
            self.execute(sql)
        except sqlite3.OperationalError as oe:
            print oe
            raise ProgrammerGoof("%s in %s" % (oe,sql))

    # return the fields of the object joined by commas
    def fields_str(self):
        return ", ".join(self.columns.keys())

    # return the values of the object quoted and joined by commas
    # fixme: this SO breaks if the values aren't strings
    def values_str(self):
        values=[]
        for k in self.columns.keys():
            values.append(getattr(self,k) or '')
        value_str=", ".join("'%s'" % x for x in values)
        return value_str

    @classmethod
    def tablename(self):                # can be overridden, obviously
        return str(self.__name__)

    def create_index(self,*fields,**args):
        try:
            index_name=args['index_name']
        except KeyError as ke:
            index_name="_".join(fields)
        unique='UNIQUE' if 'unique' in args else ''
        index_column=", ".join(fields)
        sql="CREATE %s INDEX IF NOT EXISTS %s ON %s (%s)" % (unique, index_name, self.tablename(), index_column)
        self.execute(sql)

    def column_info(self):
        sql="select * from sqlite_master where type='table' and name=?"
        self.execute(sql,self.tablename())
        row=self.cursor.fetchone()
        create_sql=row[4]
        mg=re.search("\(([^)]+)\)",create_sql)
        guts=mg.group(1)
        info={}
        for col in guts.split(", "):
            stuff=col.split(" ")
            f=stuff[0]
            t=stuff[1]
            info[f]=t

        return info

            
        
    
    def table_exists(self):
        try:
            sql="SELECT COUNT(*) FROM %s" % self.tablename()
            self.execute(sql)
            return True
        except sqlite.OperationalError:
            return False

    
