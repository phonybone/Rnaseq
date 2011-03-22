import sys, exceptions, traceback, yaml

__all__=["warn","die","UserError","ProgrammerGoof","ConfigError","MissingArgError"]

def warn(*a):
    args=list(a)                        # so we can append to an empty list if need be
    if (len(args)==0):
        args.append("something's wrong")
    sys.stderr.write("\n".join(map(str,args)))
    sys.stderr.write("\n")

def die(*args):
    warn(*args)
    sys.exit(1)

class RnaseqException(Exception):
    show_traceback=True


class UserError(RnaseqException):
    show_traceback=False

class ConfigError(RnaseqException):
    show_traceback=False

class ProgrammerGoof(RnaseqException):
    pass

class MissingArgError(ProgrammerGoof):
    pass

########################################################################
# testing
if __name__ == "__main__":

    warn(Exception("exception fred"))

    try:
        f=open("/this/file/is/imaginary")
    except IOError as e:
        warn(e)

    warn()
    warn("hi there")
    warn("hi there2","and something else")

    warn("about to die!")
    die("gasp!")
    
