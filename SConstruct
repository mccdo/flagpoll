import os, string, sys
import distutils.sysconfig
import distutils.util
import SCons
import SCons.Util

opts = Options()
opts.Add(PathOption('prefix', 'Directory to install under', '/usr'))
env = Environment()
opts.Update(env);
opts.Save('.scons.conf', env)

flagpoll_py = File('flagpoll.py')
flagpoll_fpc = File('flagpoll.fpc')

# Here are our installation paths:
inst_prefix = '$prefix'
inst_bin    = '$prefix/bin'
inst_data   = '$prefix/share/flagpoll'
Export('env inst_prefix inst_bin inst_data')


env.Install(inst_data, flagpoll_fpc)
env.InstallAs(os.path.join(inst_bin, 'flagpoll'), flagpoll_py)
env.Alias('install', inst_prefix)

