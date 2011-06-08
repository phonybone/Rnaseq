import re

# changes whitespace to '_';
# removes a bunch of dangerous characters from paths;
# returns the result
def sanitize(path):
    path=re.sub("\s+","_",path)
    path=re.sub("[()+$^*?<>{}\][\"'`]","",path)
    return path
