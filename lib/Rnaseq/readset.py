#-*-python-*-

import yaml, socket, os, glob, re, time
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from warn import *
from dict_helpers import scalar_values
from evoque_helpers import evoque_template
from RnaseqGlobals import RnaseqGlobals



class Readset(dict):
    '''
    Readsets define the input data for a pipeline, including both the location of
    data files and metadata.
    '''
    #required_attrs=['reads_file', 'label', 'ID']
    required_attrs=['reads_file', 'label']
    wd_time_format="%H%M%S_%d%b%y"

    def __init__(self,*args,**kwargs):
        # if there are any dicts in *args, use them to update self; allows "d={'this':'that'}; r=Readset(d)" construction
        self.paired_end=False           # may get overwritten
        for a in args:
            try:
                self.update(a)
                for k,v in a.items():
                    kwargs[k]=v
            except TypeError: pass

        for k,v in kwargs.items():
            setattr(self,k,v)
            self[k]=v

        if not hasattr(self,'format') or self.format==None: self.format='fq' # I bet this comes back to bite
        
        self.evoque_fields().resolve_reads_file().resolve_working_dir().set_ID().verify_complete()
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
                if key not in self: self[key] = other[key]
        for key in kwargs:
            if key not in self: self[key] = kwargs[key]

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
            raise ConfigError("%s contains both 'readsets' and 'reads_file' entries; only one may be present" % filename)
        elif 'readsets' not in yml and 'reads_file' not in yml:
            raise ConfigError("%s contains neither 'readsets' nor 'reads_file' entries; must have one or the other" % filename)
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
        errors=[]
        rlist=yml['readsets']
        if type(rlist) != type([]): # make sure rlist is a list
            raise ConfigError("%s: type of 'readsets' must be a list; got '%s'" % (filename, type(rlist)))
        for ryml in rlist:
            if type(ryml)!=type({}): # make sure elements of rlist are dicts
                raise ConfigError("%s: elements of readsets must be dicts (hashes); got '%s'" % (filename, type(ryml)))

            ryml.update(scalars)
            try:
                rs=self.load_glob(ryml,filename)[0]
            except ConfigError as ce:
                errors.append(str(ce))
                continue

            rs.update(scalars)
            readset_objs.append(rs)

        if len(errors)>0:
            raise ConfigError("%s:\n"%filename+"\n".join(errors))

        return readset_objs


    # returns a list of one Readset object based on the file glob contained in yml['reads_file']
    @classmethod
    def load_glob(self,yml,filename):
        try: reads_files=yml['reads_file']
        except KeyError:
            try: reads_files=yml['reads_files']
            except KeyError: raise ConfigError("%s: readset does not define reads_file(s)" % filename)

        # get the reads directory, if present
        try: reads_dir=yml['reads_dir']
        except KeyError: reads_dir=os.getcwd() # fixme: hope this is right thing to do

        # hack?
        reads_dir=evoque_template(reads_dir, RnaseqGlobals.config['rnaseq']) # in case of ${root_dir}
        #print "lg: reads_dir is %s" % reads_dir
        
        files=[]
        globlist=re.split('[\s,]+',reads_files)
        missing=[]
        for fglob in globlist:
            if not os.path.isabs(fglob):
                fglob=os.path.normpath(os.path.join(reads_dir, fglob))
            
            filelist=glob.glob(fglob)
            if len(files)==0:
                missing.append("%s: no matching files for %s" % (filename, fglob))
            files.extend(filelist)

        if len(files)==0:
            msg=", ".join(missing)
            raise ConfigError(msg)


        # Make the Readset object:
        #print "load_glob: files is %s" % files
        scalars=scalar_values(yml)
        scalars['filename']=filename
        scalars['reads_files']=files
        return [Readset(scalars)]

    ########################################################################
    # attempt to resolve ${} vars listed in readset files with values from
    # RnaseqGlobals.config['rnaseq'].  Mostly there for ${root_dir}.
    def evoque_fields(self):
        vars=self.__dict__
        vars.update(RnaseqGlobals.conf_value('rnaseq'))
        
        for a in dir(self):
            if a.startswith('__'): continue
            attr=getattr(self,a)
            if type(attr) != type(''): continue
            if not re.search('\$\{', attr): continue

            try: setattr(self, a, evoque_template(attr, vars))
            except NameError: pass

        return self

    ########################################################################
    # set self.reads_file so that it includes self.reads_dir if necessary:
    # Does this handle paired-end or multiple filenames?
    def resolve_reads_file(self,filename=None):
        # get self.reads_file:
        try:
            reads_file=self.reads_file
            if reads_file == None:
                raise ConfigError("no reads_file 1")
        except: 
            raise ConfigError("no reads_file 2")

        # try to verify that only one reads file is present, even if paired end input.
        # Can't really set self.reads_file if more than one present
        try:
            if len(self.reads_files) > 1:
                self.reads_file=self.reads_files[0]
                return self
        except AttributeError:
            pass

        try:                            # use self.reads_dir if it exists:
            reads_dir=self.reads_dir
            #print "rrf: got reads_dir: %s" % reads_dir
            if (os.path.isabs(reads_file)):
                raise ConfigError("%s: reads_file (%s) cannot be absolute in presence of reads_dir (%s)" % (filename, reads_file, reads_dir))
            self.reads_file=os.path.join(reads_dir, reads_file)

        except AttributeError as e:     # otherwise use os.getcwd():
            self.reads_dir=os.getcwd()
            #print "rrf: setting reads_dir to %s" % self.reads_dir
            self.reads_file=os.path.join(self.reads_dir, reads_file)

        if not hasattr(self,'reads_files'): # this can happen if Readset(**kwargs) is called manually, not through load(), as in testing
            self.reads_files=[self.reads_file] # assumes just one reads_file
            #print "rrf: setting reads_files to %s (from self.reads_file)" % self.reads_files 
        return self


    ########################################################################

    # returns a "fixed" version of working_dir
    # guarantees that self.working_dir is set
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

        try: label=self.label
        except: label=None


        # append label if present:
#        try: working_dir=os.path.join(working_dir, self.label)
#        except AttributeError: pass

        self.working_dir=working_dir
        return self

    # set self.ID and self.id
    # we only set self.ID if:
    # a) there is exactly 1 reads_file, or
    # b) there are two reads_files, self.paired_end is True, and the filenames are verified to be of the right format
    #
    # This must be called *after* self.resolve_working_dir()
    # returs self
    def set_ID(self, *ID):
        # try to assign self.ID from ID[0], which might not be there:
        try: self.ID=ID[0]
        except IndexError: pass

        # see if self.ID exists, and if it does, is it an absolute path.  If so, do nothing
        try:
            if os.path.isabs(self.ID): pass
            else: self.ID=os.path.join(self.working_dir, self.ID) # self.ID exists and is relative

        except AttributeError: 
            # self.ID didn't exist, set to combination of working_dir and basename of reads_file
            if len(self.reads_files)==1:
                ID=os.path.join(self.working_dir,os.path.basename(self.reads_file))
                ID=re.sub('\..*$', '', ID)
                self.ID=ID
            elif len(self.reads_files)==2 and self.paired_end:
                # check that file names are of proper form:
                mg=re.search('^(.*)_[12]\.[\w_]+$', os.path.basename(self.reads_files[0])) # works of self.reads_files[0]...
                error_msg="'%s' isn't a well-formed filename for paired_end data: must match '_[12].<ext>'" % self.reads_files[0]
                try:
                    self.ID=os.path.join(self.working_dir, mg.groups()[0])
                except IndexError:
                    raise ConfigError(error_msg)
                except AttributeError:
                    raise ConfigError(error_msg)
                
            else:
                if RnaseqGlobals.conf_value('verbose') or RnaseqGlobals.conf_value('debug'):
                    print >>sys.stderr, "Cannot set ID: too many files (%d), paired_end=%s" % (len(self.reads_files), self.paired_end)
                return self
            


        # 
        #self['ID']=self.ID              # god dammit

        # set self.id as ...something.  why?
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
