import unittest, os, sys

if os.path.dirname(__file__)=='':       # running in local directory
    root_dir=(os.path.normpath(os.getcwd()+'/../..'))
else:
    root_dir=(os.path.normpath(os.path.dirname(__file__)+'/../..'))
sys.path.append(os.path.join(root_dir, 'lib'))
sys.path.append(os.path.join(root_dir, 'ext_libs'))


from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

# Test the various combinations of working_dir, reads_dir and reads_file, and the
# generated attribute ID.

class TestLoad(unittest.TestCase):
    def setUp(self):
        RnaseqGlobals.initialize(__file__, testing=True)
        #templated.template_dir=RnaseqGlobals.root_dir()+"/../../fixtures/templates"
        self.readset_dir=os.path.join(RnaseqGlobals.root_dir(),'t/fixtures/readsets')

    def test_list(self):
        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset12.syml'
        rlist=Readset.load(readset_file)
        self.assertEqual(type(rlist),type([]))
        self.assertEqual(len(rlist),12)

        for rs in rlist:
            self.assertEqual(rs.org, 'mouse')
            self.assertEqual(rs.readlen, 75)
            self.assertEqual(os.path.dirname(rs.reads_file), self.readset_dir)
            self.assertTrue(re.match('s_\d\d?_\d_sequence.txt',os.path.basename(rs.reads_file)))
            self.assertTrue(re.search(rs.label,os.path.basename(rs.reads_file)))
            self.assertEqual(rs.label,rs.description)


    def test_glob_rel(self):
        readset_file=RnaseqGlobals.root_dir()+'/t/fixtures/readsets/readset_rel_glob.syml'
        rlist=Readset.load(readset_file)
        self.assertEqual(len(rlist),1)
        filelist=rlist[0].reads_files
        self.assertEqual(len(filelist), 3)
        for i in range(1,3):
            filename="s_%d_export.txt" % i
            found=False
            for f in filelist:
                if re.search(filename, f):
                    found=True
                    break
            self.assertTrue(found)

    # don't know how to test absolute globs because we don't know where installation directory
    # will be.  fixme.
    def test_glob_abs(self):
        pass

    # test readset.resolve_working_dir
    def test_wd_rel_rel(self):
        rs=Readset(reads_file='subdir/some_data.txt',working_dir='some_dir', label='label')
        self.assertEqual(rs.working_dir, os.path.join(os.getcwd(),'subdir/some_dir'))
        self.assertEqual(rs.ID, os.path.join(os.getcwd(),'subdir','some_dir/some_data.txt'))
        self.assertEqual(rs.id, 'some_data.txt')

    def test_wd_rel_abs(self):
        rs=Readset(reads_file='subdir/some_data.txt',working_dir='/some_dir', label='label')
        self.assertEqual(rs.working_dir, '/some_dir')
        self.assertEqual(rs.ID, '/some_dir/some_data.txt')

    def test_wd_rel_none(self):
        rs=Readset(reads_file='subdir/some_data.txt',working_dir=None, label='label')
        self.assertEqual(rs.working_dir, os.path.join(os.getcwd(),'subdir'))
        self.assertEqual(rs.ID, os.path.join(os.getcwd(),'subdir/some_data.txt'))

    def test_wd_abs_rel(self):
        rs=Readset(reads_file='/some/subdir/some_data.txt',working_dir='some_dir', label='label')
        self.assertEqual(rs.working_dir, '/some/subdir/some_dir')
        self.assertEqual(rs.ID, '/some/subdir/some_dir/some_data.txt')

    def test_wd_abs_abs(self):
        rs=Readset(reads_file='/some/subdir/some_data.txt',
                   working_dir='/some/other/dir',
                   label='label')
        self.assertEqual(rs.working_dir, '/some/other/dir')
        self.assertEqual(rs.ID, '/some/other/dir/some_data.txt')

    def test_wd_abs_none(self):
        rs=Readset(reads_file='/some/subdir/some_data.txt',working_dir=None, label='label')
        self.assertEqual(rs.working_dir, '/some/subdir')
        self.assertEqual(rs.ID, '/some/subdir/some_data.txt')


    def test_glob(self):
        dir=os.path.dirname(__file__)
        if dir=='': dir=os.getcwd()
        dir=os.path.abspath(dir+'/../fixtures/readsets')
        os.chdir(dir)
        rlist=Readset.load('readset_rel_glob.syml')
        self.assertEqual(type(rlist),type([]))
        self.assertEqual(len(rlist),1)

        for rs in rlist:
            #print "rs.label is %s" % rs.label
            self.assertEqual(rs.label, 'rel_glob') # not really what we want, I think... They should be different
        

    def test_wd_timestamp(self):
        reads_file='/some/subdir/some_data.txt'
        rs=Readset(reads_file=reads_file,working_dir='timestamp', label='label')
        ts=time.strftime(Readset.wd_time_format)
        self.assertEqual(rs.working_dir, '/some/subdir/%s' % ts)

        reads_file='subdir/some_data.txt'
        rs=Readset(reads_file=reads_file, working_dir='timestamp', label='label')
        ts=time.strftime(Readset.wd_time_format)
        self.assertEqual(rs.working_dir, os.path.join(os.getcwd(),os.path.dirname(reads_file),ts))

        
        
suite = unittest.TestLoader().loadTestsFromTestCase(TestLoad)
unittest.TextTestRunner(verbosity=2).run(suite)
