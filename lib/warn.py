import sys
import exceptions

__all__=["warn","die"]

def warn(*a):
    args=list(a)                        # so we can append to an empty list if need be
    if (len(args)==0):
        args.append("something's wrong")
    sys.stderr.write("\n".join(map(str,args)))
    sys.stderr.write("\n")

def die(*args):
    warn(*args)
    sys.exit(1)

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
    
