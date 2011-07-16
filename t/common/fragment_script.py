from RnaseqGlobals import *

# read a sh script contained in filename
# break the script up into step fragments
# return a dict: k=step name, v=script fragment

def fragment_script(filename):
    # read cufflinks sh script:

    f=open(filename)
    cufflinks_script=f.read()
    f.close()
    #print "cufflinks_script is %d bytes long" % len(cufflinks_script)

    # parse script into fragments based on step name; store fragments to hash:
    stepname=''
    fragment=''
    script_fragments={}
    lines=cufflinks_script.split("\n")
    for line in lines:
        if re.match('#+$',line): continue
        mg=re.match('# step ([\s\w()]+):\s*', line)
        if mg:
            if stepname != '':
                script_fragments[stepname]=fragment.strip()
                fragment=''
            stepname=mg.group(1)
            stepname=re.sub('\([^)]*\)','',stepname) # remove stuff in ()'s
            stepname=re.sub('\s*$', '', stepname) # trim trailing whitespace

        # append next line to fragment:
        if stepname!='':
            fragment+=line+"\n"

    if 'footer' not in script_fragments:
        script_fragments['footer']=fragment.strip()

    return script_fragments

def first_diff(s1,s2):
    min_len=len(s1)
    if len(s2)<min_len: min_len=len(s2)
    i=0
    while i<min_len:
        if s1[i]!=s2[i]: return i
        i+=1
    return -1


def diff_strs(s1,s2,l=15):
    fd=first_diff(s1,s2)
    if fd==-1: return ('','')
    if fd>5: fd-=5
    return (s1[fd:fd+l], s2[fd:fd+l])
    
