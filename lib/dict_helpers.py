# return a dict comprised of any key/value pair in d where type(v) is one of the scalar types (ie string, int, float)
def scalar_values(d):
    scalars=dict()
    for k,v in d.items():
        if type(v)==type('') or type(v)==type(1) or type(v)==type(1.0) or type(v)==type(True):
            scalars[k]=v
    return scalars

