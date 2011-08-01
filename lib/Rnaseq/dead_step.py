    ########################################################################
    ########################################################################
    # Dead code
    dead_code='''

    # If a step needs more than one line to invoke (eg bowtie: needs to set an environment variable),
    # define the set of commands in a template and set the 'sh_template' attribute to point to the template
    # within the templates/sh_templates subdir).  This routine fetches the template and calls evoque on it, and
    # returns the resulting string.
    # If no sh_template is required, return None.
    def sh_script_old(self, **kwargs):
        try: sh_template=self.sh_template
        except: return None
        
        template_dir=os.path.join(RnaseqGlobals.root_dir(),"templates","sh_template")
        domain=Domain(template_dir, errors=4)
        template=domain.get_template(sh_template)
        
        vars={}
        vars.update(self.__dict__)
        vars.update(self)
        try: vars.update(self.pipeline[self.name])
        except: pass

        #vars['readset']=self.pipeline.readset # fixme: really? used by some steps, eg mapsplice
        vars['sh_cmd']=self.sh_cmdline()
        vars['config']=RnaseqGlobals.config
        vars['ID']=self.pipeline.ID()

        try:
            vars.update(self.pipeline.step_exports)
        except AttributeError as ae:
            pass

        vars.update(kwargs)

        try:
            script=template.evoque(vars)
        except NameError as ne: 
            #print "%s.sh_script() not ok (ne=%s)" % (self.name, ne)
            raise ConfigError("%s while processing step '%s'" %(ne,self.name))

        return script

    # use the self.usage formatting string to create the command line that executes the script/program for
    # this step.  Return as a string.  Throws exceptions as die()'s.
    def sh_cmdline_old(self):
        usage=self.usage()


        # evoque the cmd str:
        domain=Domain(os.getcwd(), errors=4) # we actually don't care about the first arg
        domain.set_template(self.name, src=usage)
        tmp=domain.get_template(self.name)
        vars={}
        vars.update(self.__dict__)
#        vars.update(self.pipeline)
        vars.update(RnaseqGlobals.config)

        try: vars.update(self.pipeline[self.name])
        except: pass

        try: vars.update(self.pipeline.step_exports) # fixme: still need this?
        except: pass

        try: cmd=tmp.evoque(vars)
        except AttributeError as ae:
            raise ConfigError(ae)
        return cmd


    # 
#     def __setitem__(self,k,v):
#         super(Step,self).__setitem__(k,v) # call dict.__setitem__()
#         if hasattr(self,k):
#             if callable(getattr(self,k)):
#                 m=getattr(self,k)
#                 m(v)
#         else:
#             setattr(self,k,v)

#     # update() and setdefault() taken from http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
#     def update(self, *args, **kwargs):
#         if args:
#             if len(args) > 1:
#                 raise TypeError("update expected at most 1 arguments, got %d" % len(args))
#             other = dict(args[0])
#             for key in other:
#                 self[key] = other[key]
#         for key in kwargs:
#             self[key] = kwargs[key]

#     def setdefault(self, key, value=None):
#         if key not in self:
#             self[key] = value
#         return self[key]


#     def __setattr__(self,attr,value):
#         super(Step,self).__setattr__(attr,value) # call dict.__setattr__()
#         self.__dict__[attr]=value


    '''

    ########################################################################
    def inputs_old(self):
        try: return re.split("[,\s]+",self.input)
        except: return []

    def outputs_old(self):
        try: return re.split("[,\s]+",self.output)
        except: return []
    
    def creates_old(self):
        try: return re.split("[,\s]+",self.create)
        except: return []
    
    
