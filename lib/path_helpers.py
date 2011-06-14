import re, os

# changes whitespace to '_';
# removes a bunch of dangerous characters from paths;
# returns the result
def sanitize(path):
    path=re.sub("\s+","_",path)
    path=re.sub("[()+$^*?<>{}\][\"'`]","",path)
    return path

def exists_on_path(basename, dir_list, permission=os.R_OK):
    if type(dir_list) == type(""):
        dir_list=dir_list.split(":")
    if type(dir_list) != type([]):
        raise ProgrammerGoof("%s: wrong type %s (should be list)" % (dir_list, type(dir_list)))

    for dir in dir_list:
        full_path=os.path.abspath(os.path.join(dir, basename))
        if os.access(full_path, permission): return True
    return False

    
    
