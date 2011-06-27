import unittest
from Rnaseq import *
from RnaseqGlobals import RnaseqGlobals
from warn import *
from templated import *

# Test the various combinations of working_dir, reads_dir and reads_file, and the
# generated attribute ID.

class TestLoad(unittest.TestCase):
    def setUp(self):
        templated.template_dir=os.path.normpath(os.path.abspath(__file__)+"/../../fixtures/templates")
        RnaseqGlobals.initialize(__file__, testing=True)
        

    def test_list(self):
        readset_file=os.path.abspath(os.path.dirname(__file__)+'../readsets/readset12.syml')
        rlist=Readset.load(readset_file)
        self.assertEqual(type(rlist),type([]))
        self.assertEqual(len(rlist),12)

        for rs in rlist:
            self.assertEqual(rs.org, 'mouse')
            self.assertEqual(rs.readlen, 75)
            self.assertEqual(os.path.dirname(rs.reads_file), '/some/path/to/data')
            self.assertTrue(re.match('s_\d\d?_\d_sequence.txt',os.path.basename(rs.reads_file)))
            self.assertTrue(re.search(rs.label,os.path.basename(rs.reads_file)))
            self.assertEqual(rs.label,rs.description)


    def test_glob_rel(self):
        readset_file=os.path.abspath(os.path.dirname(__file__)+'../readsets/readset_rel_glob.syml')
        rlist=Readset.load(readset_file)
        for rs in rlist:
            self.assertTrue(re.match('s_\d\d?_export.txt',os.path.basename(rs.reads_file)))

    # don't know how to test absolute globs because we don't know where installation directory
    # will be.  fixme.
    def test_glob_abs(self):
        pass

    # test readset.resolve_working_dir
    def test_wd_rel_rel(self):
        rs=Readset(reads_file='subdir/some_data.txt',working_dir='some_dir', label='label')
        self.assertEqual(rs.working_dir, os.path.join(os.getcwd(),'some_dir'))
        self.assertEqual(rs.ID, os.path.join(os.getcwd(),'some_dir','some_data.txt'))

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
        self.assertEqual(len(rlist),3)

        for rs in rlist:
            self.assertEqual(rs.label, 'rel_glob') # not really what we want, I think... They should be different
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(TestLoad)
unittest.TextTestRunner(verbosity=2).run(suite)
