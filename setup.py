needed_libs=['optparse', 'sqlalchemy', 'yaml', 'evoque']
for lib in needed_libs:
    print "checking %s" % lib
    __import__(lib)
