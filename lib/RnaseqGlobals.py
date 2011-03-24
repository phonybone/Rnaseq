#-*-python-*-
import os, sys, optparse, yaml

class RnaseqGlobals():
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
        return argv

    # return parsed argv
    @classmethod
    def parse_cmdline(self):                    
        parser=optparse.OptionParser(self.usage)

        parser.add_option('--cluster',       dest='use_cluster', action='store_true', default=False)
        parser.add_option("-f","--config",   dest="config_file",   help="specify alternative config file",
                          default=os.path.normpath(os.path.abspath(__file__)+"/../../config/rnaseq.conf.yml"))
        parser.add_option("-p","--pipeline", dest="pipeline_name", help="pipeline name")
        parser.add_option("--pipeline_script", dest="pipeline_scriptname", help="specify alternative name for pipeline shell script",
                          default="rnaseq_pipeline.sh")
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
