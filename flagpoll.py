#!/usr/bin/env python

#    -----------------------------------------------------------------
#
#    Flag Poll: A tool to extract flags from installed applications
#    for compiling, settting variables, etc.
#
#    Original Authors:
#       Daniel E. Shipton <dshipton@gmail.com>
#
#    Flag Poll is Copyright (C) 2006 by Daniel E. Shipton
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to:
#    Free SoftwareFoundation, Inc.
#    51 Franklin Street, Fifth Floor, 
#    Boston, MA  02110-1301  USA
#
#    -----------------------------------------------------------------


from optparse import OptionParser
import sys, os, glob, os.path, copy, platform
pj = os.path.join


####################################################################
# SNAGGED FROM PYTHON 2.4 for versions under 2.4
####################################################################
import re as _re
class _multimap:
    """Helper class for combining multiple mappings.

    Used by .{safe_,}substitute() to combine the mapping and keyword
    arguments.
    """
    def __init__(self, primary, secondary):
        self._primary = primary
        self._secondary = secondary

    def __getitem__(self, key):
        try:
            return self._primary[key]
        except KeyError:
            return self._secondary[key]

class _TemplateMetaclass(type):
    pattern = r"""
    %(delim)s(?:
      (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
      (?P<named>%(id)s)      |   # delimiter and a Python identifier
      {(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
      (?P<invalid>)              # Other ill-formed delimiter exprs
    )
    """

    def __init__(cls, name, bases, dct):
        super(_TemplateMetaclass, cls).__init__(name, bases, dct)
        if 'pattern' in dct:
            pattern = cls.pattern
        else:
            pattern = _TemplateMetaclass.pattern % {
                'delim' : _re.escape(cls.delimiter),
                'id'    : cls.idpattern,
                }
        cls.pattern = _re.compile(pattern, _re.IGNORECASE | _re.VERBOSE)

class Template:
    """A string class for supporting $-substitutions."""
    __metaclass__ = _TemplateMetaclass

    delimiter = '$'
    idpattern = r'[_a-z][_a-z0-9]*'

    def __init__(self, template):
        self.template = template

    # Search for $$, $identifier, ${identifier}, and any bare $'s

    def _invalid(self, mo):
        i = mo.start('invalid')
        lines = self.template[:i].splitlines(True)
        if not lines:
            colno = 1
            lineno = 1
        else:
            colno = i - len(''.join(lines[:-1]))
            lineno = len(lines)
        raise ValueError('Invalid placeholder in string: line %d, col %d' %
                         (lineno, colno))

    def substitute(self, *args, **kws):
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kws
        elif kws:
            mapping = _multimap(kws, args[0])
        else:
            mapping = args[0]
        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                val = mapping[named]
                # We use this idiom instead of str() because the latter will
                # fail if val is a Unicode containing non-ASCII characters.
                return '%s' % val
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)

    def safe_substitute(self, *args, **kws):
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kws
        elif kws:
            mapping = _multimap(kws, args[0])
        else:
            mapping = args[0]
        # Helper function for .sub()
        def convert(mo):
            named = mo.group('named')
            if named is not None:
                try:
                    # We use this idiom instead of str() because the latter
                    # will fail if val is a Unicode containing non-ASCII
                    return '%s' % mapping[named]
                except KeyError:
                    return self.delimiter + named
            braced = mo.group('braced')
            if braced is not None:
                try:
                    return '%s' % mapping[braced]
                except KeyError:
                    return self.delimiter + '{' + braced + '}'
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                return self.delimiter
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)
####################################################################
# End Snagging
####################################################################

class Utils:
   # Holds collection of small utility functions
   
   def getFlagpollVersion():
      FLAGPOLL_MAJOR_VERSION = 0
      FLAGPOLL_MINOR_VERSION = 1
      FLAGPOLL_PATCH_VERSION = 5
      return ( FLAGPOLL_MAJOR_VERSION, FLAGPOLL_MINOR_VERSION, FLAGPOLL_PATCH_VERSION )
   getFlagpollVersion = staticmethod(getFlagpollVersion)

   def getPathList():
      #TODO: expand LD_LIBRARY_PATH to 64/32/etc???
      pkg_cfg_dir = []
      flg_cfg_dir = []
      ld_path = []

      if os.environ.has_key("PKG_CONFIG_DIR"):
         pkg_cfg_dir = os.environ["PKG_CONFIG_DIR"].split(os.pathsep)

      if os.environ.has_key("FLG_CONFIG_DIR"):
         flg_cfg_dir = os.environ["FLG_CONFIG_DIR"].split(os.pathsep)

      if os.environ.has_key("LD_LIBRARY_PATH"):
         ld_path = os.environ["LD_LIBRARY_PATH"].split(os.pathsep)
         ld_path = [pj(p,'pkgconfig') for p in ld_path if os.path.exists(p)]         

      path_list = ["/usr/lib64/pkgconfig", "/usr/lib/pkgconfig", "/usr/share/pkgconfig"]
      path_list = [p for p in path_list if os.path.exists(p)]
      path_list.extend(pkg_cfg_dir)
      path_list.extend(flg_cfg_dir)
      path_list.extend(ld_path)
      flagDBG().out(flagDBG.INFO, "Utils.getPathList",
                    "Using path list: " + str(path_list))
      return path_list
   getPathList = staticmethod(getPathList)

   def stripDupInList(gen_list):
      new_list = []
      for item in gen_list:
         if item not in new_list:
            if len(item) > 0:
               new_list.append(item)
      return new_list
   stripDupInList = staticmethod(stripDupInList)

   def stripDupLinkerFlags(flag_list):
      # List is constructed as such ("-L /path", "-L/sfad", "-fpge", "-l pg", "-lpg")
      # We do slightly dumb stripping though
      lib_list = []
      dir_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in lib_list and flg not in dir_list:
            if len(flg) > 0:
               if flg.startswith("-L") or flg.startswith("-R"):
                  dir_list.append(flg)
               else:
                  lib_list.append(flg)
      new_list = dir_list + lib_list
      return new_list
   stripDupLinkerFlags = staticmethod(stripDupLinkerFlags)

   def stripDupIncludeFlags(flag_list):
      # List is constructed as such ("-I/inc", "-fno-static-blah")
      # We do slightly dumb stripping though
      inc_list = []
      extra_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in inc_list and flg not in extra_list:
            if len(flg) > 0:
               if flg.startswith("-I"):
                  inc_list.append(flg)
               else:
                  extra_list.append(flg)
      extra_list.sort()
      new_list = inc_list + extra_list
      return new_list
   stripDupIncludeFlags = staticmethod(stripDupIncludeFlags)

   def cflagsOnlyDirIncludeFlags(flag_list):
      # List is constructed as such ("-I/inc", "-fno-static-blah")
      # We do slightly dumb stripping though
      inc_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in inc_list:
            if len(flg) > 0:
               if flg.startswith("-I"):
                  inc_list.append(flg)
      return inc_list
   cflagsOnlyDirIncludeFlags = staticmethod(cflagsOnlyDirIncludeFlags)

   def cflagsOnlyOtherIncludeFlags(flag_list):
      # List is constructed as such ("-I/inc", "-fno-static-blah")
      # We do slightly dumb stripping though
      extra_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in extra_list:
            if len(flg) > 0:
               if not flg.startswith("-I"):
                  extra_list.append(flg)
      return extra_list
   cflagsOnlyOtherIncludeFlags = staticmethod(cflagsOnlyOtherIncludeFlags)

   def libsOnlyLinkerFlags(flag_list):
     # List is constructed as such ("-L /path", "-L/sfad", "-fpge", "-l pg", "-lpg")
      # We do slightly dumb stripping though
      lib_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in lib_list:
            if len(flg) > 0:
               if flg.startswith("-l"):
                  lib_list.append(flg)
      return lib_list
   libsOnlyLinkerFlags = staticmethod(libsOnlyLinkerFlags)      

   def libsOnlyOtherLinkerFlags(flag_list):
     # List is constructed as such ("-L /path", "-L/sfad", "-fpge", "-l pg", "-lpg")
      # We do slightly dumb stripping though
      other_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in other_list:
            if len(flg) > 0:
               if not flg.startswith("-l") and not flg.startswith("-L") and not flag.startswith("-R"):
                  other_list.append(flg)
      return other_list
   libsOnlyOtherLinkerFlags = staticmethod(libsOnlyOtherLinkerFlags) 

   def libDirsOnlyLinkerFlags(flag_list):
     # List is constructed as such ("-L /path", "-L/sfad", "-fpge", "-l pg", "-lpg")
      # We do slightly dumb stripping though
      dir_list = []
      for flg in flag_list:
         flg = flg.strip()
         if flg not in dir_list:
            if len(flg) > 0:
               if flg.startswith("-L") or flg.startswith("-R"):
                  dir_list.append(flg)
      return dir_list
   libDirsOnlyLinkerFlags = staticmethod(libDirsOnlyLinkerFlags) 

   def printList(gen_list):
      list_string = ""
      for item in gen_list:
         if len(item) > 0:
            list_string+=str(item)
            list_string+=" "
      print list_string
   printList = staticmethod(printList)

   def parsePcFile(filename):
      lines = open(filename).readlines()
      vars = {}
      locals = {}
      for line in lines:
       line = line.strip()
       if not line:
         continue
       elif ':' in line: # exported variable
         name, val = line.split(':', 1)
         name = name.strip()
         val = val.strip()
         if '$' in val:
           try:
             val = Template(val).safe_substitute(locals)
           except ValueError:
            flagDBG().out(flagDBG.ERROR, "PkgInfo.parse", "%s has an invalid .pc file" % self.mName)
         vars[name] = val
       elif '=' in line: # local variable
         name, val = line.split('=', 1)
         name = name.strip()
         val = val.strip()
         if '$' in val:
           try:
             val = Template(val).safe_substitute(locals)
           except ValueError:
            flagDBG().out(flagDBG.ERROR, "PkgInfo.parse", "%s has an invalid .pc file" % self.mName)
         locals[name] = val
      return vars
   parsePcFile = staticmethod(parsePcFile)


class flagDBG(object):
#      Logging class is really easy to use
#      Levels:
#      0 - VERBOSE
#      1 - INFO
#      2 - WARN
#      3 - ERROR

   VERBOSE=0
   INFO=1
   WARN=2
   ERROR=3

   __initialized = False

   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance

   def __init__(self):
      if flagDBG.__initialized:
         return
      flagDBG.__initialized = True
      self.mLevel = self.WARN
      self.mLevelList = ["VERBOSE","INFO","WARN","ERROR"]

   def setLevel(self, level):
      if level <= 3:
         self.mLevel = level

   def out(self, level, obj, message):
      if level >= self.mLevel: 
         print self.mLevelList[level] + ":" + str(obj) + ": " + str(message)
      if level == self.ERROR:
         sys.exit(1)


class DepResolutionSystem(object):
   """ You add PkgAgents with Filters into system and call resolve()
       you can check for succes by depsSatisfied() and get the list
       of packages that work back by calling getPackages()
   """

   __initialized = False
   
   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance

   def __init__(self):
      if DepResolutionSystem.__initialized:
         return
      DepResolutionSystem.__initialized = True
      self.mResolveAgents = []
      self.mAgentDict = {}
      self.mFilters = []
      self.mResolveAgentFilters = []
      self.mInvalidPackageList = []
      self.mSatisfied = False
      self.mAgentChangeList = [] # list of those responsible for adding Filters
                                 # to agents in higher in the chain than them
                                 # these are the first agents to ask that they pick
                                 # the next best package of them
      self.mAgentsVisitedList = [] # list of Agents that have been visited
      self.mResolvedPackageList = [] # list that is generated when deps are satified
      self.mCheckPrivateRequires = False

   def getFilters(self):
      return self.mFilters

   def addFilter(self, filter):
      self.mFilters.append(filter)

   def addResolveAgentFilter(self, filter):
      self.mResolveAgentFilters.append(filter)

   def makeRequireFilter(self, requires):
      arch_list = []
      arch_list.append("no_arch")
      arch_list.append("")
      if platform.system() == "Linux":
         if requires == "64":
            arch_list.append("x86_64")
         if requires == "32":
            arch_list.append("i386")
            arch_list.append("i586")
            arch_list.append("i686")
      if platform.system() == "Darwin":
         if requires == "64":
            arch_list.append("ppc64")
         if requires == "32":
            arch_list.append("ppc")
      
      new_filter = Filter("Arch", lambda x: x in arch_list)
      self.addFilter(new_filter)


   def createAgent(self, name):
      if self.checkAgentExists(name):
         return self.getAgent(name)
      else:
         agent = PkgAgent(name)
         flagDBG().out(flagDBG.INFO, "DepResSys.createAgent", "Adding %s" % name)
         self.addNewAgent(agent)
         return agent

   def setPrivateRequires( self, req ):
      self.mCheckPrivateRequires = req

   def checkPrivateRequires(self):
      return self.mCheckPrivateRequires

   def checkAgentExists(self, name):
      return self.mAgentDict.has_key(name)

   def getAgent(self, name):
      if self.mAgentDict.has_key(name):
         return self.mAgentDict[name]
      else:
         flagDBG().out(flagDBG.ERROR, "DepResSys.getAgent", "Agent %s does not exist" % name)

   def addNewAgent(self, agent):
      self.mAgentDict[agent.getName()] = agent

   def addResolveAgent(self, agent):
      if agent not in self.mResolveAgents:
         self.mResolveAgents.append(agent)
         for filt in self.mResolveAgentFilters:
            agent.addFilter(filt)

   def isSatisfied(self):
      return self.mSatisfied

   def updateResolvedPackages(self):
      pkg_list = []
      agent_list = []
      for agent in self.mResolveAgents:
         list = agent.getCurrentPackageList(agent_list)
         pkg_list.extend(list)
      self.mResolvedPackageList = pkg_list
      

   def getPackages(self):
      flagDBG().out(flagDBG.VERBOSE, "DepResSys.getPackages",
                    "Generating list of valid packages ")
                    #str([pkg.getCurrentPa.getName() for pkg in self.mResolvedPackageList]))
      # If this comes back empty then there isn't a valid set of packages to use
      self.updateResolvedPackages()
      return self.mResolvedPackageList

   def checkFiltersChanged(self):
      list_to_use = []
      return True in [pkg.filtersChanged(list_to_use) for pkg in self.mResolveAgents] 

   def resolveHelper(self):
      self.resolveAgentsChanged = True
      while self.resolveAgentsChanged:
         for agent in self.mResolveAgents:
            flagDBG().out(flagDBG.VERBOSE, "DepResSys.resolveHelper",
                          "Updating " + agent.getName())
            agent.update(self.mAgentsVisitedList, self.mAgentChangeList)
         self.resolveAgentsChanged = self.checkFiltersChanged()

   # Ask mResolveAgents if they are done(they ask sub people) unless they are
   # really above you in the walk
   # If there were changes...run update on mResolveAgents again
   # at the end ask for pkglist..if it comes back empty then we don't
   # have a usable configuration for those packages
   def resolveDeps(self):
      self.resolveHelper() 
      self.updateResolvedPackages()
      # Check if the first round through we found something
      # Otherwise we need to start removing packages that aren't viable
      # during the loop
      self.mSatisfied = (len(self.mResolvedPackageList) != 0)      
      
      # remove top of packages that added Filters.
      # then move on to resolving again
      # remove more if neccesary
      agentChangeNumber = 0
      while not self.mResolvedPackageList:
         if(self.mAgentChangeList[agentChangeNumber]):
            if self.mAgentChangeList[agentChangeNumber] in self.mInvalidPackageList:
               agentChangeNumber+=1
            else:
               if(self.mAgentChangeList[agentChangeNumber].getViablePackages()):
                  flagDBG().out(flagDBG.VERBOSE, "DepResSys.resolveDeps",
                                "Removing bad pkg from " +
                                self.mAgentChangeList[agentChangeNumber].getName())
                  self.mInvalidPackageList.append(self.mAgentChangeList[agentChangeNumber].removeCurrentPackage())
               else:
                  flagDBG().out(flagDBG.VERBOSE, "DepResSys.resolveDeps",
                                "No combinations.. Resetting " +
                                self.mAgentChangeList[agentChangeNumber].getName())
                  self.mAgentChangeList[agentChangeNumber].reset()
                  agentChangeNumber+=1
         self.resolveHelper() 
         self.updateResolvedPackages()
         self.mSatisfied = (len(self.mResolvedPackageList) != 0)      
      return

class PkgAgent:
   """ Agent that keeps track of the versions for a package given some filters
       and the addition of Filters
   """

   #   Makes a PkgAgent that finds its current package with the version reqs
   def __init__(self, name):
      if DepResolutionSystem().checkAgentExists(name):
         flagDBG().out(flagDBG.ERROR, "PkgAgent", "Package Agent %s already exists" % self.mName)
         
      self.mName = name
      flagDBG().out(flagDBG.VERBOSE, "PkgAgent", "Creating:" + str(self.mName))

      if not PkgDB().exists(name):
         flagDBG().out(flagDBG.ERROR, "PkgAgent", "No info for package: %s" % self.mName)

      DepResolutionSystem().addNewAgent(self)
      self.mFilterList = DepResolutionSystem().getFilters()
      self.mBasePackageList = PkgDB().getPkgInfos(name)
      for filt in self.mFilterList:
         self.mBasePackageList = filt.filter(self.mBasePackageList)

      if len(self.mBasePackageList) == 0:
         flagDBG().out(flagDBG.ERROR, "PkgAgent", "No viable packages for: %s" % self.mName)
         

      self.mViablePackageList = copy.deepcopy(self.mBasePackageList)
      if self.mViablePackageList:
         self.mCurrentPackage = self.mViablePackageList[0]
      else:
         self.mCurrentPackage = []
      self.mAgentDependList = [] # Agents that it depends on/needs to update
      self.makeDependList()
      self.mFiltersChanged = True

   def getName(self):
      return self.mName

   #Filter("Version", lambda x: x == "4.5")
   def makeDependList(self):
      dep_list = []
      if self.mCurrentPackage:
         req_string = self.mCurrentPackage.getVariable("Requires")
         if DepResolutionSystem().checkPrivateRequires():
            req_string = req_string + " " + self.mCurrentPackage.getVariable("Requires.private")
         req_string = req_string.strip()
         if req_string == "":
            return
         req_string = req_string.replace(',', ' ')
         req_string = req_string.replace('(', ' ')
         req_string = req_string.replace(')', ' ')
         space_req_string_list = req_string.split(' ')
         req_string_list = []
         for entry in space_req_string_list:
            if len(entry) > 0:
               req_string_list.append(entry)
         i = 0
         flagDBG().out(flagDBG.INFO, "PkgAgent.makeDependList",
                       self.mCurrentPackage.getName() + " requires: " + str(req_string_list))
         while len(req_string_list) > i:
            if PkgDB().exists(req_string_list[i]):
               new_filter = []
               new_agent = DepResolutionSystem().createAgent(req_string_list[i])
               if len(req_string_list) > i+1:
                  if req_string_list[i+1] == "=":
                     ver_to_filt = req_string_list[i+2]
                     new_filter = Filter("Version", lambda x: x == ver_to_filt)
                  elif req_string_list[i+1] == "<=":
                     ver_to_filt = req_string_list[i+2]
                     new_filter = Filter("Version", lambda x: x <= ver_to_filt)
                  elif req_string_list[i+1] == ">=":
                     ver_to_filt = req_string_list[i+2]
                     new_filter = Filter("Version", lambda x: x >= ver_to_filt)
                  else:
                     i+=1
               else:
                  i+=1
               dep_list.append(new_agent)
               if new_filter:
                  i+=3
                  new_agent.addFilter(new_filter)
            else:
               flagDBG().out(flagDBG.ERROR, "PkgAgent.makeDependList",
                             "Package %s depends on %s but is not seem to be installed." % (self.mName, str(req_string_list[i])))

         flagDBG().out(flagDBG.VERBOSE, "PkgAgent.makeDependList", 
                       "List is:" + str([pkg.getName() for pkg in dep_list]))
      self.mAgentDependList = dep_list

   def filtersChanged(self,packageList):
      tf_list = [self.mFiltersChanged]
      if self.mName not in packageList:
         packageList.append(self.mName)
         for pkg in self.mAgentDependList:
            tf_list.append(pkg.filtersChanged(packageList))
      return True in tf_list

   def getCurrentPackageList(self, packageList):
      pkgs = []
      if self.mName not in packageList:
         flagDBG().out(flagDBG.VERBOSE, "PkgAgent.getCurrentPackageList",
                       "Package: %s" % self.mName)
         pkgs.append(self.mCurrentPackage)
         packageList.append(self.mName)
         for pkg in self.mAgentDependList:
            pkgs.extend(pkg.getCurrentPackageList(packageList))
      return pkgs

   # current pkginfo for me
   def getCurrentPkgInfo(self):
      return self.mCurrentPackage

   # Someone else usually places these on me
   # I keep track of those separately
   def addFilter(self, filter):
      flagDBG().out(flagDBG.VERBOSE, "PkgAgent.addFilter",
                    "Adding a Filter to %s" % self.mName)
      self.mFiltersChanged = True
      self.mFilterList.append(filter)

   def removeCurrentPackage(self):
      flagDBG().out(flagDBG.VERBOSE, "PkgAgent.removeCurrentPackage",
                    "Removing current package of %s" % self.mName)
      if self.mViablePackageList:
         ret_val = self.mViablePackageList[0] in self.mBasePackageList
         del mViablePackageList[0]
         if self.mViablePackageList:
            self.mCurrentPackage = self.mViablePackageList[0]
         return ret_val

   def update(self, agentVisitedList, agentChangeList):
      if self.mName in agentVisitedList:
         return

      agentVisitedList.append(self.mName)

      if self.mFiltersChanged:
         self.mFiltersChanged = False
         self.updateFilters()

      # TODO: checkFilters and add them
      # if a pkg is in visitedList then add yourself to agentChangeList
      
      for pkg in self.mAgentDependList:
         pkg.update(agentVisitedList, agentChangeList)
      return

   def updateFilters(self):
      for filt in self.mFilterList:
         self.mViablePackageList = filt.filter(self.mViablePackageList)
      if len(self.mViablePackageList) > 0:
         self.mCurrentPackage = self.mViablePackageList[0]
      else:
         self.mCurrentPackage = []
      

   def reset(self):
      flagDBG().out(flagDBG.VERBOSE, "PkgAgent.reset", "Resetting package: %s" % self.mName)
      self.mViablePackageList = self.mBasePackageList
      if self.mViablePackageList:
         self.mCurrentPacakge = self.mViablePackageList[0]
      else:
         self.mCurrentPackage = []
      self.mFilterList = self.mBaseFilters
      self.mAgentDependList = []
      self.mFiltersChanged = True
      return

class Filter:
   """ A single Filter that knows how to filter the list it recieves
       Will be inheireted....?..?
   """
   
   def __init__(self, variableName, testCallable):
      self.mVarName = variableName
      self.mTestCallable = testCallable
      
   def filter(self, pkg_info_list):
      ret_pkg_list = []
      
      # Filter first
      for pkg in pkg_info_list:
         var = pkg.getVariable(self.mVarName)
         if self.mTestCallable(var):
            ret_pkg_list.append(pkg)
            
      # Now sort
      ret_pkg_list.sort(lambda lhs,rhs: cmp(lhs.getVariable(self.mVarName),
                                            rhs.getVariable(self.mVarName)))
      
      return ret_pkg_list

#requires: qt == 4.5

#Filter("Version", lambda x: x <= "4.5")
#Filter("Version", lambda x: x <= "4.5")
   
class PkgDB(object):
   """ Holds all the neccesary information to evaluate itself when needed.
       Is in charge of holding a list of PkgInfo's that contain info
       about the package.
   """
   
   __initialized = False
   
   def __init__(self):
      if self.__initialized:
         return
      self.__initialized = True
      self.mPkgInfos = {}           # {pkg_name: List of package infos}
      self.populatePkgInfoDBPcFiles()
      self.populatePkgInfoDBFpcFiles()

   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance
      
   def getVariables(self, name, variable_list):
      flagDBG().out(flagDBG.INFO, "PkgDB.getVariable", 
                    "Finding " + str(variable_list) + " in " + str(name))
      ret_list = []
      for var in variable_list:
         if self.mPkgInfos.has_key(name):
            ret_list.extend(self.mPkgInfos[name][0].getVariable(var))
         else:
            flagDBG().out(flagDBG.ERROR, "PkgDB.getVariable", "Package %s not found." % name)
      return ret_list
         
   def getVariablesAndDeps(self, pkg_list, variable_list):
      flagDBG().out(flagDBG.INFO, "PkgDB.getVariablesAndDeps", 
                    "Finding " + str(variable_list) + " in " + str(pkg_list))
      
      if DepResolutionSystem().checkPrivateRequires():
         temp_var_list = []
         for var in variable_list:
            temp_var_list.append(var.join(".private"))
         variable_list = variable_list + temp_var_list
      
      for name in pkg_list:
         if self.mPkgInfos.has_key(name):
            agent = DepResolutionSystem().createAgent(name)
            DepResolutionSystem().addResolveAgent(agent)
         else:
            flagDBG().out(flagDBG.ERROR, "PkgDB.getVariablesAndDeps", "Package %s not found." % name)

      DepResolutionSystem().resolveDeps()
      pkgs = DepResolutionSystem().getPackages()
      var_list = []
      for pkg in pkgs:
         if pkg:
            for var in variable_list:
               var_list.extend(pkg.getVariable(var).split(' '))

      return var_list

   def getPkgInfos(self, name):
      if self.mPkgInfos.has_key(name):
         return self.mPkgInfos[name]
      else:
         flagDBG().out(flagDBG.ERROR, "PkgDB.getPkgInfos", "Package %s not found." % name)
              
   def exists(self, name):
      return self.mPkgInfos.has_key(name)

   def getInfo(self, name):
      if self.mPkgInfos.has_key(name):
         return [pkg.getInfo() for pkg in self.mPkgInfos[name]]
      else:
         flagDBG().out(flagDBG.ERROR, "PkgDB.getInfo", "Package %s not found." % name)

   def buildPcFileDict(self):
      """ Builds up a dictionary of {name: list of files for name} """
      pc_dict = {}
      for p in Utils.getPathList():
         glob_list = glob.glob(os.path.join(p, "*.pc")) # List of .pc files in that directory
         flagDBG().out(flagDBG.VERBOSE, "PkgDB.buildPcFileDict",
                       "Process these pc files: %s" % str(glob_list))
         for g in glob_list: # Get key name and add file to value list in dictionary
            key = os.path.basename(g)[:-3]   # Strip .pc off the filename...rstrip no worky
            pc_dict.setdefault(key,[]).append(g)
      return pc_dict # { "key", [ "list", "of", "corresponding", "pc", "files"] }

   def populatePkgInfoDBPcFiles(self):
      dict_to_pop_from = self.buildPcFileDict()
      for (pkg,files) in dict_to_pop_from.iteritems():
         self.mPkgInfos.setdefault(pkg,[]).append(PkgInfo(pkg, files[0], "pc"))

   def buildFpcFileList(self):
      """ Builds up a dictionary of {name: list of files for name} """
      file_list = []
      for p in Utils.getPathList():
         glob_list = glob.glob(os.path.join(p, "*.fpc")) # List of .pc files in that directory
         flagDBG().out(flagDBG.VERBOSE, "PkgDB.buildPcFileDict",
                       "Process these fpc files: %s" % str(glob_list))
         for g in glob_list:
            file_list.append(g)
      return file_list # [ "list", "of", "fpc", "files"] 

   def populatePkgInfoDBFpcFiles(self):
      list_to_add = self.buildFpcFileList()
      for file in list_to_add:
         var_dict = Utils.parsePcFile(file)
         if not var_dict.has_key("Provides"):
            flagDBG().out(flagDBG.ERROR, "PkgDB.populate", "%s missing Provides" % str(file))
         if not var_dict.has_key("Arch"):
            flagDBG().out(flagDBG.ERROR, "PkgDB.populate", "%s missing Arch" % str(file))
         provides_string = var_dict["Provides"]
         provides_string = provides_string.replace(',', ' ')
         provides_string = provides_string.replace('(', ' ')
         provides_string = provides_string.replace(')', ' ')
         for key in provides_string.split(" "):
            if len(key) > 0:
               self.mPkgInfos.setdefault(key,[]).append(PkgInfo(key, file, "fpc", var_dict))

class PkgInfo:
   """ Holds the information for a package file on the system. These however
       are evaluated when the need arises.
   """

   def __init__(self, name, file, type, varDict={}):
      self.mName = name
      self.mFile = file
      self.mIsEvaluated = False
      self.mType = type
      self.mVariableDict = varDict
      if self.mType == "fpc":
         self.mIsEvaluated = True
      

   def getVariable(self, variable):
      self.evaluate()
      return self.mVariableDict.get(variable,"")      

   def getName(self):
      return self.mName

   def evaluate(self):
      if not self.mIsEvaluated:
         flagDBG().out(flagDBG.INFO, "PkgInfo.evaluate", "Evaluating %s" % self.mName)
         self.mVariableDict= Utils.parsePcFile(self.mFile)
         self.mIsEvaluated = True
   
   def getInfo(self):
      self.evaluate()
      return self.mVariableDict

class OptionsEvaluator:
   
   def __init__(self):
      self.mOptParser = self.GetOptionParser()
      (self.mOptions, self.mArgs) = self.mOptParser.parse_args()
      if self.mOptions.version:
         print "%s.%s.%s" % Utils.getFlagpollVersion()
         sys.exit(0)
      if len(self.mArgs) < 1:
         self.mOptParser.print_help()
         sys.exit(1)

   def evaluateArgs(self):

      if self.mOptions.debug:
         flagDBG().setLevel(flagDBG.VERBOSE)
         Utils.printList(PkgDB().getInfo(self.mArgs[0]))

      if self.mOptions.require:
         DepResolutionSystem().makeRequireFilter(self.mOptions.require)

      if self.mOptions.exists:
         print PkgDB().exists(self.mArgs[0])

      if self.mOptions.info:
         for pkg in self.mArgs:
            Utils.printList(PkgDB().getInfo(pkg))

      if self.mOptions.variable:
         Utils.printList(Utils.stripDupInList(PkgDB().getVariablesAndDeps(self.mArgs, [self.mOptions.variable])))

      if self.mOptions.static:
         DepResolutionSystem().setPrivateRequires(True)

      if self.mOptions.atleast_version:
         atleast_version = self.mOptions.atleast_version
         atleast_filter = Filter("Version", lambda x: x >= atleast_version)
         DepResolutionSystem().addResolveAgentFilter(atleast_filter)
         
      if self.mOptions.max_release:
         max_release = self.mOptions.max_release
         max_filter = Filter("Version", lambda x: x.startswith(max_release))
         DepResolutionSystem().addResolveAgentFilter(max_filter)
         
      if self.mOptions.exact_version:
         exact_version = self.mOptions.exact_version
         exact_filter = Filter("Version", lambda x: x == exact_version)
         DepResolutionSystem().addResolveAgentFilter(exact_filter)

      if self.mOptions.modversion:
         print PkgDB().getVariables(self.mArgs[0], ["Version"])
         
      if self.mOptions.libs:
         Utils.printList(Utils.stripDupLinkerFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Libs"])))

      if self.mOptions.libs_only_l:
         Utils.printList(Utils.libsOnlyLinkerFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Libs"])))

      if self.mOptions.libs_only_L:
         Utils.printList(Utils.libDirsOnlyLinkerFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Libs"])))

      if self.mOptions.libs_only_other:
         Utils.printList(Utils.libsOnlyOtherLinkerFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Libs"])))

      if self.mOptions.cflags:
         Utils.printList(Utils.stripDupIncludeFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Cflags"])))

      if self.mOptions.cflags_only_I:
         Utils.printList(Utils.cflagsOnlyDirIncludeFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Cflags"])))

      if self.mOptions.cflags_only_other:
         Utils.printList(Utils.cflagsOnlyOtherIncludeFlags(PkgDB().getVariablesAndDeps(self.mArgs, ["Cflags"])))

#      if not self.mOptions.list_all:
#        print PkgDB().getPkgList



   def GetOptionParser(self):
      parser = OptionParser()
      parser.add_option("--modversion", action="store_true", dest="modversion", 
                        help="output version for package")
      parser.add_option("--version", action="store_true", dest="version", 
                        help="output version of pkg-config")
      parser.add_option("--require", dest="require", 
                        help="adds additional requirements for packages ex. 32/64")
      parser.add_option("--libs", action="store_true", dest="libs", 
                        help="output all linker flags")
      parser.add_option("--static", action="store_true", dest="static", 
                        help="output linker flags for static linking")
      #parser.add_option("--short-errors", action="store_true", dest="short_errors", 
      #                  help="print short errors")
      parser.add_option("--libs-only-l", action="store_true", dest="libs_only_l", 
                        help="output -l flags")
      parser.add_option("--libs-only-other", action="store_true", dest="libs_only_other", 
                        help="output other libs (e.g. -pthread)")
      parser.add_option("--libs-only-L", action="store_true", dest="libs_only_L", 
                        help="output -L flags")
      parser.add_option("--cflags", action="store_true", dest="cflags", 
                        help="output all pre-processor and compiler flags")
      parser.add_option("--cflags-only-I", action="store_true", dest="cflags_only_I", 
                        help="output -I flags")
      parser.add_option("--cflags-only-other ", action="store_true", dest="cflags_only_other", 
                        help="output cflags not covered by the cflags-only-I option")
      parser.add_option("--exists", action="store_true", dest="exists", 
                        help="return 0 if the module(s) exist")
      #parser.add_option("--list-all", action="store_true", dest="list_all", 
      #                  help="list all known packages")
      parser.add_option("--debug", action="store_true", dest="debug", 
                        help="show verbose debug information")
      parser.add_option("--info", action="store_true", dest="info", 
                        help="show information for packages")
      #parser.add_option("--print-errors", action="store_true", dest="print_errors", 
      #                  help="show verbose information about missing or conflicting packages")
      #parser.add_option("--silence-errors", action="store_true", dest="silence_errors", 
      #                  help="show no information about missing or conflicting packages")
      #parser.add_option("--uninstalled", action="store_true", dest="uninstalled", 
      #                  help="return 0 if the uninstalled version of one or more module(s) or their dependencies will be used")
      #parser.add_option("--errors-to-stdout", action="store_true", dest="errors_to_stdout", 
      #                  help="print errors from --print-errors to stdout not stderr")
      #parser.add_option("--print-provides", action="store_true", dest="print_provides", 
      #                  help="print which packages the package provides")
      #parser.add_option("--print-requires", action="store_true", dest="print_requires", 
      #                  help="print which packages the package requires")
      parser.add_option("--atleast-version", dest="atleast_version", 
                        help="return 0 if the module is at least version ATLEAST_VERSION")
      parser.add_option("--exact-version", dest="exact_version", 
                        help="return 0 if the module is exactly version EXACT_VERSION")
      parser.add_option("--max-release", dest="max_release", 
                        help="return 0 if the module has a release that has a version of MAX_RELEASE and will return the max")
      #parser.add_option("--atleast-pkgconfig-version=VERSION", dest="atleast_pkgconfig_version", 
      #                  help="require given version of pkg-config")
      parser.add_option("--variable", dest="variable", 
                        help="get the value of a variable")
      #parser.add_option("--define-variable", dest="define_variable", 
      #                  help="set the value of a variable")
      return parser


def main():
   # GO!
   # Initialize singletons and the start evaluating
   my_dbg = flagDBG()
   my_dep_system = DepResolutionSystem()
   opt_evaluator = OptionsEvaluator()
   opt_evaluator.evaluateArgs()
   sys.exit(0)

if __name__ == "__main__":
   main()
