import re
def sanitize(path):
    path=re.sub("\s+","_",path)
    path=re.sub("[()+$^*?<>{}\][\"'`]","",path)
    return path
