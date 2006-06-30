import os, string, sys
import distutils.sysconfig
import distutils.util
import SCons
import SCons.Util

opts = Options()
baseEnv = {}
PREFIX = ARGUMENTS.get('prefix', '/usr')
opts.Update(baseEnv);

env = Environment()
flagpoll_py = File('flagpoll.py')


env.InstallAs(os.path.join(PREFIX, 'bin/flagpoll'), flagpoll_py)
env.Alias('install', os.path.join(PREFIX, 'bin/flagpoll'))
if os.path.exists(os.path.join(PREFIX, 'bin/flagpoll')):
   os.chmod(os.path.join(PREFIX,'bin/flagpoll'), 0755)
