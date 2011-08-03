#-*-python-*-

import yaml, socket, os, glob, re, time
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from warn import *
from dict_helpers import scalar_values
from evoque_helpers import evoque_template
from RnaseqGlobals import RnaseqGlobals

class Readset(dict):
    required_attrs=['reads_file', 'label', 'ID']
    wd_time_format="%H%M%S_%d%b%y"

    def __init__(self,*args,**kwargs):
        # if there are any dicts in *args, use them to update self; allows "d={'this':'that'}; r=Readset(d)" construction
        for a in args:
            try:
                self.update(a)
                for k,v in a.items():
                    kwargs[k]=v
            except TypeError: pass

        for k,v in kwargs.items():
            setattr(self,k,v)
            self[k]=v

        self.resolve_reads_file().resolve_working_dir().set_ID().verify_complete()
        self.exports=['org','readlen','working_dir','reads_file','label','format','ID']


########################################################################

    def __str__(self):
        str=''
        for k,v in self.items():
            str+="%s: %s\n" % (k,v)
        return str

    def __setitem__(self,k,v):
        super(Readset,self).__setitem__(k,v) # call dict.__setitem__()
        super(Readset,self).__setattr__(k,v)

    def __setattr__(self,attr,value):
        super(Readset,self).__setattr__(attr,value) # call dict.__setattr__()
        super(Readset,self).__setitem__(attr,value)

    # update() and setdefault() taken from http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    ########################################################################

    __tablename__='readset'

    @classmethod
    def create_table(self, metadata, engine):
        readset_table=Table(self.__tablename__, metadata,
                            Column('id',Integer, primary_key=True),
                            Column('reads_file', String),
                            Column('org', String),
                            Column('readlen', Integer),
                            Column('working_dir', String),
                            useexisting=True,
                         )
        metadata.create_all(engine)
        mapper(Readset, readset_table)
        return readset_table
        
    ########################################################################

    # return a list of Readset objects as determined by
    # the contents of filename.  Files can either define
    # a list of readset objects, or they can define a
    # set of files (in a list of file globs)
    @classmethod
    def load(self,filename):
        try:
            f=open(filename)
            yml=yaml.load(f)
            f.close()
        except IOError as ioe:
            raise UserError(str(ioe))
        except AttributeError as ae:
            raise ProgrammerGoof(ae)
        except yaml.scanner.ScannerError as se:
            msg='''
There was an error in the readset file %s:\n%s.
This file must be in correct YAML format.  Please carefully check the file and correct the error.
See http://en.wikipedia.org/wiki/YAML#Sample_document for details and examples.
'''
            msg = msg % (filename, str(se))
            raise ConfigError(msg)

        if 'readsets' in yml and 'reads_file' in yml:
            raise ConfigError("%s contains both 'readsets' and 'reads_files' entries; only one may be present" % filename)
        elif 'readsets' not in yml and 'reads_file' not in yml:
            raise ConfigError("%s contains neither 'readsets' nor 'reads_files' entries; must have one or the other" % filename)
        elif 'readsets' in yml:           # contains a list of readsets
            rlist=self.load_list(yml,filename)
        elif 'reads_file' in yml:       # contains a glob and/or list of files (single block)
            rlist=self.load_glob(yml,filename)
        else:
            raise "wtf?"

        return rlist

    # factory method to return an array of readset objects when yaml contains a 
    @classmethod
    def load_list(self,yml,filename):
        # make a dict from the k/v pairs in yml where type(v) is a scalar (string or number)
        scalars=scalar_values(yml)
        scalars['filename']=filename

        readset_objs=[]
        rlist=yml['readsets']
        if type(rlist) != type([]): # make sure rlist is a list
            raise ConfigError("%s: type of 'readsets' must be a list; got '%s'" % (filename, type(rlist)))
        for r in rlist:
            if not type(r)==type({}): # make sure elements of rlist are dicts
                raise ConfigError("%s: elements of readsets must be dicts (hashes); got '%s'" % (filename, type(r)))
            r.update(scalars)
            readset_objs.append(Readset(r))
        return readset_objs


    #
    @classmethod
    def load_glob(self,yml,filename):
        reads_file=yml['reads_file']

        try: reads_dir=yml['reads_dir']
        except KeyError:
            reads_dir=os.getcwd() # fixme: hope this is right thing to do
            
        # make one readset object for each path described in reads_file (which can contain glob chars):
        scalars=scalar_values(yml)      # select scalar values from yml
        scalars['filename']=filename
        try: del scalars['reads_dir']        # otherwise the constructor will barf
        except KeyError: pass

        readset_objs=[]
        for reads_file in re.split('[\s,]+',yml['reads_file']):
            path=os.path.join(reads_dir,reads_file) # build the full path
            path=evoque_template(path, self.__dict__, root_dir=RnaseqGlobals.root_dir())
            rlist=glob.glob(path)       # get all glob matches
            for rf in rlist:
                rsd=scalars.copy()
                rsd['reads_file']=rf
                rs=Readset(rsd)
                rs.reads_dir=reads_dir  # put it back
                readset_objs.append(rs)

        if len(readset_objs)==0:
            raise ConfigError("%s: no matches for %s" % (filename, os.path.join(reads_dir,yml['reads_file']))) # 
        return readset_objs

    # Does this handle paired-end or multiple filenames?
    def resolve_reads_file(self,filename=None):
        try:
            reads_file=self.reads_file
            if reads_file == None:
                raise ConfigError("no reads_file")
        except: 
            raise ConfigError("no reads_file")

        
        try:
            reads_dir=self.reads_dir
            if (os.path.isabs(reads_file)):
                raise ConfigError("%s: reads_file (%s) cannot be absolute in presence of reads_dir (%s)" % (filename, reads_file, reads_dir))
            self.reads_file=os.path.join(reads_dir, reads_file)

        except AttributeError as e:
            self.reads_dir=os.getcwd()
            self.reads_file=os.path.join(self.reads_dir, reads_file)

        return self


    def verify_paired_end_filenames(self):
        '''for paired end reads, verify self.reads_file defines exactly two files'''
        # Return if self.paired_end not defined or if set to false
        try:
            if not self.paired_end:
                return self
        except AttributeError: return self 

        # reads_file can be comma separated list or file glob
        # try glob first:
        rlist=glob.glob(self.reads_file)
        if len(rlist) != 2:
            rlist=re.split('[\s,]+',self.reads_file)
        if len(rlist) != 2:
            raise ConfigError("reads_file: '%s' is not a list or file glob defining exactly two files" % self.reads_file)

        # reads_file correctly defines two files; are the filenames in the correct format?
        errors=[]
        for fn in rlist:
            if not re.search('_[12]\.[\w_]$', fn):
                errors.append("%s is ill-formed: must contain _1 or _2 followed by .<suffix>" % fn)
        if len(errors) != 0:
            raise ConfigError("\n".join(errors))
        return self
            

    # returns a "fixed" version of working_dir
    def resolve_working_dir(self):
        reads_file=self.reads_file
        try: working_dir=self.working_dir
        except: working_dir=None

        if os.path.isabs(reads_file):
            if working_dir==None:
                working_dir=os.path.dirname(reads_file)
            elif os.path.isabs(working_dir):
                pass                    # working_dir remains the same
            elif working_dir=='timestamp':
                ts=time.strftime(Readset.wd_time_format)
                working_dir=os.path.join(os.path.dirname(reads_file),ts)
            else:                      
                working_dir=os.path.join(os.path.dirname(reads_file),working_dir)
                
        else:                           # reads_file is relative
            if working_dir==None:
                working_dir=os.path.join(os.getcwd(),os.path.dirname(reads_file))
            elif working_dir=='timestamp':
                ts=time.strftime(Readset.wd_time_format)
                working_dir=os.path.join(os.getcwd(),os.path.dirname(reads_file),ts)
            elif os.path.isabs(working_dir):
                pass
            else:
                working_dir=os.path.join(os.getcwd(),working_dir)

        self.working_dir=working_dir
        return self

    # set self.ID and self.id
    # must be called *after* self.resolve_working_dir()
    # returs self
    def set_ID(self, *ID):
        # try to assign self.ID from ID[0], which might not be there:
        try: self.ID=ID[0]
        except IndexError: pass

        # see if self.ID exists, and if it does, is it an absolute path.  If so, do nothing
        try:
            if os.path.isabs(self.ID):
                pass
            else:
                self.ID=os.path.join(self.working_dir, self.ID) # self.ID is relative
        except AttributeError: 
            self.ID=os.path.join(self.working_dir,os.path.basename(self.reads_file)) # self.ID didn't exist

        self['ID']=self.ID              # god dammit

        # set self.id as 
        self.id=os.path.basename(self.ID)
        self['id']=self.id
        return self
                

    def verify_complete(self, filename=None):
        if filename==None:
            try: filename=self.filename
            except: filename='unknown'
        missing=[]
        for attr in self.required_attrs:
            if not hasattr(self,attr): missing.append(attr)
        if len(missing) > 0:
            raise UserError(("The readset in %s is missing required fields:\n\t - " % filename) + "\n\t - ".join(missing))
        return self

    ########################################################################

    def get_email(self):
        try:
            return self.email
        except AttributeError:
            user=os.environ['USER']
            suffix=".".join(socket.gethostname().split('.')[-2:])
            return "@".join((user,suffix))

    ########################################################################
    # Dead Code:
    ########################################################################

    def path_iterator_deadcode(self):
        try:
            l=glob.glob(self['reads_files'])
        except Exception:
            l=glob.glob(self['reads_file']) # danger! will get overwritten!

        l.sort()
        return l


    def readsfile_deadcode(self,*args):
        try: self['reads_file']=args[0]
        except IndexError: pass
        return self['reads_file']

    def next_reads_file_deadcode(self):
        try: path_it=self.current_path_list
        except AttributeError: setattr(self,'current_path_list',self.path_iterator())

        try: next_rf=self.current_path_list[0]
        except IndexError: return None

        del self.current_path_list[0]
        return next_rf
