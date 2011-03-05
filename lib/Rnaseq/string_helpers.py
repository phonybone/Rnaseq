__all__=['extract']

def extract(s,d):
    mg=re.findall('%\((\w+)\)',s)
    d2={}
    for m in mg:
        d2[m]=d[m]                      # throws KeyError
    return s % d2
