import re
from string import capwords

def dash2camel_case(str):
    return re.sub('_','',capwords(str,'_'))
