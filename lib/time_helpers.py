# return a string describing the difference between two times.  t1 and t2 are integers or floats as
# returned by time.time()
def duration(t1, t2):
    t1=int(t1)
    t2=int(t2)
    duration=t1-t2
    if duration < 0: duration = -duration

    secs_in_min=60
    secs_in_hour=60*secs_in_min
    secs_in_day=24*secs_in_hour
    secs_in_year=365*secs_in_day

    l=[]
    if duration > secs_in_year:
        n=int(duration/secs_in_year)
        s='' if n==1 else 's'
        l.append("%d year%s" % (n,s))
        duration=duration%secs_in_year

    if duration > secs_in_day:
        n=int(duration/secs_in_day)
        s='' if n==1 else 's'
        l.append("%d day%s" % (n,s))
        duration=duration%secs_in_day
        
    if duration > secs_in_hour:
        n=int(duration/secs_in_hour)
        s='' if n==1 else 's'
        l.append("%d hour%s" % (n,s))
        duration=duration%secs_in_hour

    if duration > secs_in_min:
        n=int(duration/secs_in_min)
        s='' if n==1 else 's'
        l.append("%d min%s" % (n,s))
        duration=duration%secs_in_min

    s='' if duration==1 else 's'
    l.append("%d sec%s" % (duration,s))
    return ", ".join(l)

if __name__ == '__main__':
    t1=0
    for t2 in [30, 61, 234, 3292, 28329, 98238, 7372737, 48291038, 482910338]:
        print "%d: %s" % (t2, duration(t1, t2))

        
                 
    
    
