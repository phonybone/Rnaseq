#-*-python-*-
import os, sys, optparse, yaml, re
from warn import *
try:
    import sqlite3
except:
    from pysqlite2 import dbapi2 as sqlite3


    ########################################################################
    # Callbacks:

def aligner_callback(option, opt_str, value, parser):
    try:
        hash={'bowtie': { 'aligner_suffix':'fq',
                          'fq_cmd': 'solexa2fastq',
                          },
              'blat': {'aligner_suffix':'fa',
                       'fq_cmd': 'solexa2fasta',
                       },
              }
        subhash=hash[value]
    except KeyError as ke:
        raise optparse.OptionValueError("Unknown aligner: %s" % ke)

    try:
        setattr(parser.values, option.dest, value)
        suffix=subhash['aligner_suffix']
        setattr(parser.values, 'rnaseq__align_suffix', subhash['aligner_suffix'])
        setattr(parser.values, 'rnaseq__fq_cmd', subhash['fq_cmd'])
    except Exception as e:
        print "caught an %s: %s" % (type(e),e)
        raise optparse.OptionValueError(str(e))



# This should really be a singleton class
class RnaseqGlobals():
    parser=''                           # gets overwritten
    options={}
    config={}
    dbh={}
    usage=''


    @classmethod
    def initialize(self, usage, **args):
        #print "initializing RnaseqGlobals"
        self.usage=usage
        self.define_opts()
        
        opt_list=sys.argv
        try:
            opt_list.extend(args['opt_list'])
        except KeyError as ke:
            if str(ke) != "'opt_list'":
                raise ke
        (values,argv)=self.parse_cmdline(opt_list=opt_list)

        # order of checking config file: args['config_file'], values2, values
        try:
            config_file=args['config_file']
        except:
            config_file=values.config_file # blow up if this doesn't work, but shouldn't since there's a default value

        
        # set option values in config, in specific order:
        self.read_config(config_file)
        self.add_options_to_conf(values)

        # connect to database:
        db_file=os.path.join(self.conf_value('rnaseq','root_dir'), 'db', self.conf_value('db','db_name'))
        try:
            self.dbh=sqlite3.connect(db_file)
        except sqlite3.OperationalError as oe:
            raise ConfigError(str(oe)+": db_file is %s" % db_file)

        return argv


    # return parsed argv
    @classmethod
    def define_opts(self):                    
        parser=optparse.OptionParser(self.usage)
        
        # special notation: presence of '__' in dest means that options will get assigned to lower sub-hash of config
        # eg 'rnaseq__aligner'->self.config['rnaseq']['aligner']='bowtie'
        parser.add_option('--aligner',       dest='rnaseq__aligner', help="specify aligner", default="bowtie", action="callback", callback=aligner_callback, type="string")
        parser.add_option('--align_suffix',  dest='rnaseq__align_suffix', help="internal use")
        parser.add_option('--fq_cmd',        dest='rnaseq__fq_cmd',  help="internal use")
        parser.add_option('--cluster',       dest='use_cluster',     help="execute operations on a cluster (requires additional config settings)", action='store_true', default=False)
        parser.add_option("-c","--config",   dest="config_file",     help="specify alternative config file", default=os.path.normpath(os.path.abspath(__file__)+"/../../config/rnaseq.conf.yml"))
        parser.add_option("-f","--force",    dest="force",           help="force execution of pipelines and steps even if targets are up to date", action='store_true', default=False)
        parser.add_option("-p","--pipeline", dest="pipeline_name",   help="pipeline name")
        parser.add_option("-r","--readset",  dest="readset_name",    help="readset name")

        self.parser=parser


    # returns (values,args)
    @classmethod
    def parse_cmdline(self, opt_list=sys.argv):
        return self.parser.parse_args(sys.argv)

    @classmethod
    def read_config(self, config_file):
        try:
            f=open(config_file)
            yml=f.read()
            f.close()
            self.config=yaml.load(yml)

        except IOError as ioe:
            warn("error trying to load global config file:")
            die(UserError(ioe))


    @classmethod
    def add_options_to_conf(self, values):
        for o in self.parser.option_list:
            if o.dest==None: continue
            dest=str(o.dest)
            dest_path=re.split('__',dest)
            c=self.config
            for dp in dest_path[:-1]:
                c=c[dp]
            c[dest_path[-1]]=getattr(values, dest)



    

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
    def set_conf_value(self,keyslist,value):
        config=self.config
        if (type(keyslist)==type("string")):
            keyslist=[keyslist]
        for k in keyslist[:-1]:
            config=config[k]

        config[keyslist[-1]]=value
        return self

    @classmethod
    def option(self,opt):
        try:
            return self.options.opt
        except AttributeError:
            return None

#print __file__,"checking in"
