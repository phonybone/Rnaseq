from RnaseqGlobals import *

def fragment_script(filename):
    # read cufflinks sh script:
    cufflinks_file=RnaseqGlobals.root_dir()+'/t/fixtures/sh_scripts/%s' % filename 
    f=open(cufflinks_file)
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
        mg=re.match('# ([\s\w()]+):\s*', line)
        if mg:
            if stepname != '':
                script_fragments[stepname]=fragment
                fragment=''
            stepname=mg.group(1)
            stepname=re.sub('\([^)]*\)','',stepname) # remove stuff in ()'s
            stepname=re.sub('\s*$', '', stepname) # trim trailing whitespace
        fragment+=line+"\n"

    if 'footer' not in script_fragments:
        script_fragments['footer']=fragment

    return script_fragments

