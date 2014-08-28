from distutils.core import setup
import os, shutil

def copy_dlls():
    shutil.copyfile(os.path.join('bin','libsodium.dll'), os.path.join('zyrecffi', 'libsodium.dll'))
    shutil.copyfile(os.path.join('bin','libzmq.dll'), os.path.join('zyrecffi', 'libzmq.dll'))
    shutil.copyfile(os.path.join('bin','czmq.dll'), os.path.join('zyrecffi', 'czmq.dll'))
    shutil.copyfile(os.path.join('bin','zyre.dll'), os.path.join('zyrecffi', 'zyre.dll'))

copy_dlls()
setup(name='zyrecffi',
      version='0.1',
      description='cffi wrapper of zyre',
      author='Joss Gray',
      author_email='joss@jossgray.net',
      url='https://github.com/jossgray/zyrecffi',
      packages=['zyrecffi'],
      package_data= {'zyrecffi': ['*.dll']})