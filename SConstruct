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

from SCons.Script.SConscript import SConsEnvironment 	 
SConsEnvironment.Chmod = SCons.Action.ActionFactory(os.chmod, 	 
	lambda dest, mode: 'Chmod("%s", 0%o)' % (dest, mode)) 	 
  	 
def InstallPerm(env, dest, files, perm): 	 
	obj = env.InstallAs(dest, files)
	for i in obj: 	 
		env.AddPostAction(i, env.Chmod(str(i), perm))
  	 
SConsEnvironment.InstallPerm = InstallPerm 	 
  	 
# define wrappers 	 
SConsEnvironment.InstallProgram = lambda env, dest, files: InstallPerm(env, dest, files, 0755) 	 
SConsEnvironment.InstallData = lambda env, dest, files: InstallPerm(env, dest, files, 0644)

flagpoll_py = File('flagpoll')
flagpoll_fpc = File('flagpoll.fpc')

# Here are our installation paths:
inst_prefix = '$prefix'
inst_bin    = '$prefix/bin'
inst_data   = '$prefix/share/flagpoll'
Export('env inst_prefix inst_bin inst_data')


fpc_obj = env.InstallData(os.path.join(inst_data, 'flagpoll.fpc'), flagpoll_fpc)
flg_bin = env.InstallProgram(os.path.join(inst_bin, 'flagpoll'), flagpoll_py)
env.Alias('install', inst_prefix)

