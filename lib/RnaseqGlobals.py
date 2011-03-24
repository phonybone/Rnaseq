#-*-python-*-
import os, sys, optparse, yaml, re

# This should really be a singleton class
class RnaseqGlobals():
    parser=''                           # gets overwritten
    options={}
    config={}
    dbh={}
    usage=''


    @classmethod
    def initialize(self, usage):
        #print "initializing RnaseqGlobals"
        self.usage=usage
        argv=self.parse_cmdline()
        self.read_config()
        self.add_options_to_conf()
        return argv

    # return parsed argv
    @classmethod
    def parse_cmdline(self):                    
        self.parser=optparse.OptionParser(self.usage)
        parser=self.parser
        
        # special notation: presence of '__' in dest means that options will get assigned to lower sub-hash of config
        # eg 'rnaseq__aligner'->self.config['rnaseq']['aligner']='bowtie'
        parser.add_option('--aligner',       dest='rnaseq__aligner',     help="specify aligner", default="bowtie")
        parser.add_option('--cluster',       dest='use_cluster', action='store_true', default=False)
        parser.add_option("-f","--config",   dest="config_file",   help="specify alternative config file",
                          default=os.path.normpath(os.path.abspath(__file__)+"/../../config/rnaseq.conf.yml"))
        parser.add_option("-p","--pipeline", dest="pipeline_name", help="pipeline name")
        parser.add_option("-r","--readset",  dest="readset_name",  help="readset name")

        (values, args)=parser.parse_args(sys.argv)
        self.options=values
        
        
        return args                         # return remaining argv values


    @classmethod
    def read_config(self):
        try: 
            config_file=self.options.config_file
        except AttributeError:
            raise ProgrammerGoof("must call parse_cmdline() before you can call read_config()")
        
        try:
            f=open(config_file)
            yml=f.read()
            f.close()
            self.config=yaml.load(yml)

        except IOError as ioe:
            warn("error trying to load global config file:")
            die(UserError(ioe))


    @classmethod
    def add_options_to_conf(self):
        for o in self.parser.option_list:
            if o.dest==None: continue
            dest=str(o.dest)
            dest_path=re.split('__',dest)
            c=self.config
            for dp in dest_path[:-1]:
                c=c[dp]
            c[dest_path[-1]]=getattr(self.options, dest)


    

    @classmethod
    def conf_value(self,*args):
        if len(args)==0:
            raise MissingArgsException('conf_value: no args')

        conf=self.config
        for a in args:
            try:
                conf=conf[a]
            except KeyError:
                return None

        return conf

    @classmethod
    def option(self,opt):
        try:
            return self.options.opt
        except AttributeError:
            return None

#print __file__,"checking in"
