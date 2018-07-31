from distutils.core import setup, Extension
import os.path
import sys

if sys.platform == "win32" :
    include_dirs = ["C:/local/boost_1_61_0","."]
    libraries=["boost_python3-vc140-mt-1_61"]
    library_dirs=['C:/local/boost_1_61_0/lib32-msvc-14.0']
else :
    include_dirs = ["/usr/include/boost-1_61","."]
    libraries=["boost_python3"]
    library_dirs=['/usr/local/lib']


moduleRGBE = Extension('rgbe.io',
                    sources = ['sources/io.cpp'],
					library_dirs=library_dirs,
                    libraries=libraries,
                    include_dirs=include_dirs,
                    depends=[])
moduleRGBEFast = Extension('rgbe.fast',
					sources = ['sources/fast.cpp'],
					library_dirs=library_dirs,
                    libraries=libraries,
                    include_dirs=include_dirs,
                    depends=[])

setup (name = 'rgbe',
       version = '1.1',
       author='Adrien Gruson',
       author_email='adrien.gruson@irisa.fr',
       description = 'RGBE Radiance format',
       packages = ['rgbe'],
       headers = ['sources/imageerrors.h'],
       ext_modules = [moduleRGBE, moduleRGBEFast])