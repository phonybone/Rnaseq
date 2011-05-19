__all__=['extract', 'obj2dict']
import re

# find all occurences of "%(\w+)s" in a string s and use them as keys to extract from a hash.
# (essentially filters the first hash using the regex's matches as keys)
def extract(s,d):
    mg=re.findall('%\((\w+)\)',s)
    d2={}
    for m in mg:
        d2[m]=d[m]                      # throws KeyError
    return s % d2

# find all the normal-ish attributes of an object and insert them in to a dict:
def obj2dict(obj):
    l=[x for x in dir(obj) if not (re.match('__', x) or callable(getattr(obj,x)))]
    h=dict()
    for attr in l:
        h[attr]=getattr(obj,attr)
    return h
