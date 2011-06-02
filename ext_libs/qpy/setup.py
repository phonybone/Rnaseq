"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qpy/setup.py $
$Id: setup.py 31598 2009-04-29 18:51:25Z dbinger $
"""
import sys
assert sys.version >= "2.4"
sys.path.insert(0, '..')
from glob import glob
import re, os

try:
    assert 'USE_DISTUTILS' not in os.environ
    from setuptools import setup, Extension
except (ImportError, AssertionError):
    from distutils.core import setup
    from distutils.extension import Extension

from distutils.command.build_py import build_py


class qpy_build_py (build_py):

    def find_package_modules(self, package, package_dir):
        self.check_package(package, package_dir)
        module_files = (glob(os.path.join(package_dir, "*.py")) +
                        glob(os.path.join(package_dir, "*.qpy")))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)
        for f in module_files:
            abs_f = os.path.abspath(f)
            module = os.path.splitext(os.path.basename(f))[0]
            modules.append((package, module, f))
        return modules

    def build_module(self, module, module_file, package):
        if type(package) is str:
            package = package.split('.')
        elif type(package) not in (list, tuple):
            raise TypeError(
                "'package' must be a string (dot-separated), list, or tuple")
        # Now put the module source file into the "build" area.
        outfile = self.get_module_outfile(self.build_lib, package, module)
        if module_file.endswith(".qpy"):
            outfile = outfile[0:outfile.rfind('.')] + ".qpy"
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        return self.copy_file(module_file, outfile, preserve_mode=0)

    def byte_compile(self, files):
        try:
            from qpy.compile import compile_qpy_file
        except ImportError:
            build_py.byte_compile(self, files)
        else:
            existing = []
            for file in files:
                if os.path.exists(file):
                    existing.append(file)
                else:
                    alt = file[:-3] + ".qpy"
                    compile_qpy_file(alt)
                    sys.stdout.write('byte-compiling %s\n' % alt)
            build_py.byte_compile(self, existing)


if __name__ == '__main__':
    from __init__ import __version__
    if 'sdist' in sys.argv:
        if sys.platform == 'darwin':
            # Omit extended attributes from tarfile
            os.environ['COPYFILE_DISABLE'] = 'true'
        import re
        # Make sure that version numbers have all been updated.
        PAT = re.compile(r'\b%s\b' % re.escape(__version__))
        assert len(PAT.findall(open("LICENSE.txt").read())) == 14, __version__
        assert PAT.search(open("CHANGES.txt").readline()), __version__
        assert len(PAT.findall(open("README.txt").read())) == 0, __version__

        # Make sure that copyright statements are current.
        from datetime import datetime
        year = datetime.now().year # no tz, ok
        copyright = "Copyright (c) Corporation for National Research Initiatives %s" % year
        assert open("__init__.py").read().count(copyright) == 1
        assert open("README.txt").read().count(copyright) == 1
    ext_modules = [Extension(name="qpy.quoted", sources=["quoted.c"])]
    setup(
        name="qpy",
        version=__version__,
        description="xml/html content in functions",
        author="CNRI",
        author_email="webmaster@mems-exchange.org",
        url="http://www.mems-exchange.org/software/qpy/",
        license="see LICENSE.txt",
        package_dir=dict(qpy=os.curdir),
        packages=['qpy'],
        scripts=['qpcheck.py', 'qpyrun.py'],
        ext_modules=ext_modules,
        cmdclass= {'build_py': qpy_build_py},
        long_description=(
        "Qpy provides a convenient mechanism for generating safely-quoted xml "
        "from python code.  It does this by implementing a quote-no-more string "
        "data type and a slightly modified python compiler."
        ))
