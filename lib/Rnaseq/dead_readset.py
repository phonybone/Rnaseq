
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




    def load_glob(self, yml, filename)
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
