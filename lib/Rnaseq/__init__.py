#-*-python-*-

from warn import *
from dict_like import *
from templated import *
from pipeline import *
from step import *
from readset import *
from cmd_factory import *
from options import *

class Rnaseq():
    options={}
    config={}
    dbh={}
    usage=''

    # return parsed argv
    @classmethod
    def parse_cmdline(self):                    
        parser=optparse.OptionParser(self.usage)

        parser.add_option("-r","--readset",  dest="readset_name",  help="readset name")
        parser.add_option("-p","--pipeline", dest="pipeline_name", help="pipeline name")
        parser.add_option("-f","--config",   dest="config",        help="specify alternative config file",
                          default=os.path.normpath(os.path.abspath(__file__)+"/../../../config/rnaseq.conf.yml"))
        parser.add_option('--cluster',       dest='use_cluster', action='store_true', default=False)
        
        (values, args)=parser.parse_args(sys.argv)
        Rnaseq.options=values

        return args                         # return remaining argv values



