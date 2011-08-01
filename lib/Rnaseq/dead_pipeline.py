########################################################################
# Dead code:
########################################################################
    # read in the (s)yml file that defines the pipeline, passing the contents the evoque as needed.
    # load in all of the steps (via a similar mechanism), creating a list in self.steps
    # raise errors as needed (mostly ConfigError's)
    # returns self
    def load_obsolete(self):
        vars={}
        if hasattr(self,'dict'): vars.update(self.dict)
        if hasattr(self, 'readset'): vars.update(self.readset)
        vars.update(RnaseqGlobals.config)
        vars['ID']=self.ID()
        ev=evoque_dict()
        ev.update(vars)
        templated.load(self, vars=ev, final=False)
        
        # load steps.  (We're going to replace the current steps field, which holds a string of stepnames,
        # with a list of step objects.
        # fixme: explicitly add header and footer steps; 

        try:
            self.stepnames=re.split('[,\s]+',self['stepnames'])
        except AttributeError as ae:
            raise ConfigError("pipeline %s does not define stepnames" % self.name)
            
        self.steps=[]                   # resest, just in case
        for sn in self.stepnames:
            step=Step(name=sn, pipeline=self)
            assert step.pipeline==self
            # load the step's template and self.update with the values:
            try:
                vars={}
                vars.update(self.dict)
                vars.update(RnaseqGlobals.config)
                vars['ID']=self.ID()
                step.load(vars=vars)
            except IOError as ioe:      # IOError??? Where does this generate an IOError?
                raise ConfigError("Unable to load step %s" % sn, ioe)
            step.merge(self.readset)

            # add in items from step sections in <pipeline.syml>
            try:
                step_hash=self[step.name]
            except Exception as e:
                raise ConfigError("Missing section: '%s' is listed as a step name in %s, but section with that name is absent." % \
                                  (step.name, self.template_file()))
                                  
            #print "%s: step_hash is %s" % (step.name, step_hash)

            try:
                step.update(step_hash)
            except KeyError as e:
                raise ConfigError("no %s in\n%s" % (step.name, yaml.dump(self.__dict__)))

            self.steps.append(step)
            

        # Check to see that the list of step names and the steps themselves match; dies on errors
        errors=[]
        errors.extend(self.verify_steps())
        errors.extend(self.verify_continuity())
        errors.extend(self.verify_exes())
        if len(errors)>0:
            raise ConfigError("\n".join(errors))
        
        return self

    ########################################################################
    # run all step hashes through evoque if they still have ${} constrcuts:
    def fix_step_hash_old(self,step):
        try: step_hash=self[step.name]
        except: return
        
        domain=Domain(os.getcwd())
        print_flag=False
        for attr,value in step_hash.items():
            if type(value) != type(''): continue
            if not re.search('\$\{', value): continue
            #print_flag=True
            vars=evoque_dict()
            vars.update(self.readset)
            vars.update(step)
            vars.update(self.step_exports)

            domain.set_template(attr, src=value)
            tmpl=domain.get_template(attr)
            value=tmpl.evoque(vars)
            step_hash[attr]=value

        if print_flag:
            print "%s: fixed step_hash is %s" % (step.name, step_hash)
            
        self[step.name]=step_hash

                
    ########################################################################
    # check to see that all inputs and outputs connect up correctly and are accounted for
    # outputs also include files defined by "create"
    def verify_continuity_old(self):
        step=self.steps[0]
        errors=[]
        dataset2stepname={}
        
        # first step: check that inputs exist on fs, prime dataset2stepname:
        for input in step.inputs():
            if not os.path.exists(input):
                errors.append("missing inputs for %s: %s" % (step.name, input))
        for output in step.outputs():
            dataset2stepname[output]=step.name
        for created in step.creates():
            dataset2stepname[created]=step.name
            if RnaseqGlobals.conf_value('verbose'):
                print "added %s" % created

        # subsequent steps: check inputs exist in dataset2stepname, add outputs to dataset2stepname:
        for step in self.steps[1:]:        # skip first step
            #print "%s: dataset2stepname:" % step.name
            for k,v in dataset2stepname.items():
                pass
                #print "%s: %s\n" % (v,k)
            #print ""

            for input in step.inputs():
                if input not in dataset2stepname and not os.path.exists(input):
                    errors.append("pipeline '%s':\n  input %s \n  (in step '%s') is not produced by any previous step and does not currently exist" % (self.name, input, step.name))
            for output in step.outputs():
                dataset2stepname[output]=step.name
            # for created in step.creates():
                # dataset2stepname[created]=step.name

        return errors

    ########################################################################
    # get the working directory for the pipeline.
    # first ,check to see if the readset defines a working_dir
    # second, see if the pipeline itself defines a pipeline (it shouldn't)
    # each of the first two can be a directory, or a "policy".
    # valid policies include "timestamp" (and nothing else, for the moment)
    # fixme: add a check to see if a label is defined (in the readset).
    # If nothing found, use default found in config file under "default_working_dir"
    def working_dir_obsolete(self,*args):
        try: self['working_dir']=args[0]
        except IndexError: pass

        
        # (try to) get the base dir from the readset:
        try:
            readset=self.readset
            readsfile=readset.reads_file
            base_dir=os.path.dirname(readsfile)
        except KeyError as ke:
            raise UserError("Missing key: "+ke) # fixme: UserError?  really?

        # see if self['working_dir'] is defined
        try:
            wd=os.path.join(base_dir, self['working_dir'])
            return wd
        except KeyError as ie:
            pass

        # see if the readset defines a working_dir:
        try:
            wd=os.path.join(base_dir, readset['working_dir'])
            return wd
        except KeyError as ie:
            pass

        # nothing found: generate a working_dir from a timestamp:
        default='rnaseq_'+time.strftime(self.wd_time_format)
        return os.path.join(base_dir, default)



    ########################################################################
    # Determine the path of the working reads file.  Path will be
    # a combination of a working_directory and the basename of the
    # readsfile.  Final value will depend on whether the reads file
    # or the specified working directory are relative or absolute.
    # fixme: why doesn't this call self.readset.working_dir anywhere?

    def ID_obsolete(self):
        try: reads_file=self.readset.reads_file
        except KeyError: return '${ID}' # defer until later???
        except AttributeError as ae:
            if re.search("'Pipeline' object has no attribute 'readset'", str(ae)): return '${ID}'
            else:
                raise ae

        if re.search('[\*\?]', reads_file):
            raise ProgrammerGoof("%s contains glob chars; need to expand readset.path_iterator()" % reads_file)

        # try a few different things to get the working directory:
        try:
            wd=self.readset['working_dir']
            if (wd=='wd_timestamp'): wd='rnaseq_'+time.strftime(self.wd_time_format)
            #print "1. wd is %s" % wd
            
        except KeyError:
            try:
                wd=self['working_dir']
                if (wd=='wd_timestamp'): wd='rnaseq_'+time.strftime(self.wd_time_format)
                #print "2. wd is %s" % wd

            except KeyError:
                if os.path.isabs(reads_file):
                    wd=os.path.dirname(reads_file)
                    #print "3. wd is %s" % wd
                elif RnaseqGlobals.conf_value('rnaseq','wd_timestamp') or \
                     ('wd_timestamp' in self.dict and \
                      self.dict['wd_timestamp']): # -and isn't set to False
                    wd='rnaseq_'+time.strftime(self.wd_time_format)
                    #print "4. wd is %s" % wd
                
                else:
                    wd=os.getcwd()
                    #print "5. wd is %s" % wd

        if os.path.isabs(wd):
            id=os.path.join(wd,os.path.basename(reads_file)) #
            #print "6. id is %s" % id
        elif os.path.isabs(reads_file):
            id=os.path.join(os.path.dirname(reads_file), wd, os.path.basename(reads_file))
            #print "7. id is %s" % id
        else:
            id=os.path.join(os.getcwd(), wd, os.path.basename(reads_file))
            #print "8. id is %s" % id

        #self._ID=id
        #print "ID() returning %s" % id
        return id
        

    
    ########################################################################

    def new_step(self, stepname, **kwargs):
        try:
            mod=__import__('Rnaseq.steps.%s' % stepname)
        except ImportError as ie:
            raise ConfigError("error loading step '%s': %s" % (stepname, str(ie)))
        
        mod=getattr(mod,"steps")

        try:
            mod=getattr(mod,stepname)
            kls=getattr(mod,stepname)            
        except AttributeError as ae:
            raise ConfigError("step %s not defined: "+str(ae))

        # add items to kwargs:
        kwargs['pipeline']=self
        kwargs['readset']=self.readset
        step=kls(**kwargs)
        
        # If the step defines an attribute named export (fixme: and it's a list),
        # copy the step's exorted attributes to the pipeline:
        if hasattr(step,'export'):
            try:
                for attr in step.export:
                    attr_val=getattr(step,attr)
                    setattr(self,attr,attr_val)
                    self.step_exports[attr]=attr_val
            except AttributeError as ae:
                raise ConfigError("step %s tries to export missing attr '%s'" % (step.name, attr))
        
        return step

