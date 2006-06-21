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
from string import Template
import sys
import os
import glob

class flagDBG:
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

   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance

   def __init__(self):
      self.mLevel = 3
      self.mLevelList = ["VERBOSE","INFO","WARN","ERROR"]

   def setLevel(self, level):
      if level <= 4:
         self.mLevel = level

   def out(self, level, obj, message):
      if level <= self.mLevel: 
         print self.mLevelList[level] + ":" + str(obj) + ": " + str(message)

def GetFlagpollVersion():
   FLAGPOLL_MAJOR_VERSION = 0
   FLAGPOLL_MINOR_VERSION = 1
   FLAGPOLL_PATCH_VERSION = 1
   return ( FLAGPOLL_MAJOR_VERSION, FLAGPOLL_MINOR_VERSION, FLAGPOLL_PATCH_VERSION )

def GetPathList():
   #TODO: expand LD_LIBRARY_PATH and check in there
   #      look in PKG_CONFIG_DIR and in our dir?
   path_list = ["/usr/lib64/pkgconfig", "/usr/lib/pkgconfig", "/usr/share/pkgconfig"]
   flagDBG().out(flagDBG.INFO, "GetPathList", "Using path list: " + str(path_list))
   return path_list



class DepResolutionSystem(object):
   """ You add PkgAgents with constraints into system and call resolve()
       you can check for succes by depsSatisfied() and get the list
       of packages that work back by calling getPackages()
   """

   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance

   def __init__(self):
      self.mResolveAgents = []
      self.mAgents = {}
      self.mFilters = []
      self.mSatisfied = False
      self.mAgentChangeList = [] # list of those responsible for adding constraints
                                 # to agents in higher in the chain than them
                                 # these are the first agents to ask that they pick
                                 # the next best package of them
      self.mAgentsVisitedList = [] # list of Agents that have been visited
      self.mResolvedPackageList = [] # list that is generated when deps are satified


   def isSatisfied(self):
      return self.mSatisfied

   def getPackages(self):
      # If this comes back empty then there isn't a valid set of packages to use
      return self.mResolvedPackageList

   def checkConstraintsChanged(self):
      true_false_list = []
      for pkg in self.mResolveAgents:
         true_false_list.append(pkg.constraintsChanged()) 
      return True in true_false_list

   # Ask mResolveAgents if they are done(they ask sub people) unless they are
   # really above you in the walk
   # If there were changes...run update on mResolveAgents again
   # at the end ask for pkglist..if it comes back empty then we don't
   # have a usable configuration for those packages
   def resolveDeps(self):
      while self.resolveAgentsChanged:
         for agent in self.mResolveAgents:
            agent.update(self.mAgentsVisitedList, self.mAgentChangeList)
         self.resolveAgentsChanged = checkConstraintsChanged()

      # Check if the first round through we found something
      # Otherwise we need to start removing packages that aren't viable
      # during the loop
      if not mResolvedPacakgeList:
         self.mSatisfied = True
      
      # remove top of packages that added constraints.
      # then move on to resolving again
      # remove more if neccesary
      agentChangeNumber = 0
      while not self.mResolvedPackageList:
         if(self.mAgentChangeList[agentChangeNumber]):
            if(self.mAgentChangeList[agentChangeNumber].getViablePackages()):
               self.mAgentChangeList[agentChangeNumber].removeCurrentPackage()
               self.resolveDeps()
            else:
               self.mAgentChangeList[agentChangeNumber].reset()
               agentChangeNumber+=1

      return

class PkgAgent:
   """ Agent that keeps track of the versions for a package given some filters
       and the addition of constraints
   """

   #   Makes a PkgAgent that finds its current package with the version reqs
   def init(self, name, constraint_list):
      self.mName = name
      self.mBasePackageList = [] # TODO: Sorted by filters and obtained from PkgDB
      self.mViablePackageList = self.mBasePackageList
      if self.mViablePackageList:
         self.mCurrentPackage = self.mViablePackageList[0]
      else:
         self.mCurrentPackage = []
      self.mAgentDependList = [] # Agents that it depends on/needs to update
      self.mBaseConstraints = constraint_list
      self.mConstraintList = self.mBaseConstraints
      self.mConstraintsChanged = True

   def constraintsChanged(self):
      return self.mConstraintsChanged # or all its deps too...infinite recurs possible

   def getCurrentPackageList(self, packageList):
      if self.mName not in packageList:
         packageList.append(self.mName)
         for pkg in self.mAgentDependList:
            pkg.getCurrentPackageList
      return packageList

   # current pkginfo for me
   def getCurrentPkgInfo(self):
      return self.mCurrentPackage

   # Someone else usually places these on me
   # I keep track of those separately
   def addConstraint(self, constraint):
      self.mConstraintsChanged = True
      self.mConstraintList.append(constraint)

   def removeCurrentPackage(self):
      if self.mViablePackageList:
         del mViablePackageList[0]
         if self.mViablePackageList:
            self.mCurrentPackage = self.mViablePackageList[0]

   def update(self, agentVisitedList, agentChangeList):
      if self.name in agentVisitedList:
         return
      if self.mConstraintsChanged:
         self.mConstraintsChanged = False
         agentVisitedList.append(self.mName)
         # TODO: checkConstraints and add them
         # if a pkg is in visitedList then add yourself to agentChangeList
         for pkg in mAgentDependList:
            pkg.update(agentVisitedList, agentChangeList)
      return

   def reset(self):
      self.mViablePackageList = self.mBasePackageList
      if self.mViablePackageList:
         self.mCurrentPacakge = self.mViablePackageList[0]
      else:
         self.mCurrentPackage = []
      self.mConstraintList = self.mBaseConstraints
      self.mAgentDependList = []
      self.mConstraintsChanged = True
      return

class Constraint:
   """ A single constraint that knows how to enforce itself.
       Will be inheireted....?..?
   """
   
   def __init__(self, pkginfo, constraintString):
      self.mIsSatifisfied = false
      self.mPkgInfo = pkginfo
      self.mConstraintString = constraintString
      self.mRHS = []
      self.mLHS = []
      self.mLogicSymbol = []
      self.mFilteredList = []

   def filter(self, pkg_list):
      return self.mFilteredList

   def check(self):
      # TODO: check to see if constraint is satisfied
      return self.mIsSatisfied
      
   def isSatisfied(self):
      return self.mIsSatisfied

class PkgDB(object):
   """ Holds all the neccesary information to evaluate itself when needed.
       Is in charge of holding a list of PkgInfo's that contain info
       about the package.
   """

   def getVariable(self, name, variable):
      for pkg in self.mPkgInfoList:
         if(name == pkg.getName()):
            return pkg.getVariable(variable)

   def getVariableAndDeps(self, name, variable):
      for pkg in self.mPkgInfoList:
         if(name == pkg.getName()):
            return pkg.getVariable(variable)

   def getInfo(self, name):
      for pkg in self.mPkgInfoList:
         if(name == pkg.getName()):
            return pkg.getInfo()

   def __new__(type):
      if not '_the_instance' in type.__dict__:
         type._the_instance = object.__new__(type)
      return type._the_instance

   def __init__(self):
      self.mPkgInfoList = []
      self.PopulatePkgInfoDB()

   def BuildPcFileDict(self):
      """ Builds up a dictionary of {name: list of files for name} """
      pc_dict = {}
      for p in GetPathList():
         glob_list = glob.glob(os.path.join(p, "*.pc")) # List of .pc files in that directory
         for g in glob_list: # Get key name and add file to value list in dictionary
            key = os.path.basename(g)[:-3] # Strip .pc off the filename
            if pc_dict.has_key(key):
               pc_dict[key].append(g)
            else:
               pc_dict[key]=[g]
      
      return pc_dict # { "key", [ "list", "of", "corresponding", "pc", "files"] }

   def PopulatePkgInfoDB(self):
      dict_to_pop_from = self.BuildPcFileDict()
      for pkg in dict_to_pop_from:
         self.mPkgInfoList.append(PkgInfo(str(pkg), dict_to_pop_from[pkg]))

class PkgInfo:
   """ Holds the information for a package file on the system. These however
       are evaluated when the need arises.
   """

   def __init__(self, name, fileList, version="None"):
      self.mName = name
      self.mVersion = version
      self.mFileList = fileList
      self.mIsEvaluated = False
      self.mVariableDict = {}

   def getVariable(self, variable):
      self.evaluate()
      if self.mVariableDict.has_key(variable):
         return self.mVariableDict[variable]
      else:
         return ""

   def getName(self):
      return self.mName

   def evaluate(self):
      # TODO: Do more than pkg-config and parse all same name files
      if not self.mIsEvaluated:
         #print "Evaluating %s" % self.mName
         self.mVariableDict= self.parse(self.mFileList[0])
         self.mIsEvaluated = True
   
   def getInfo(self):
      self.evaluate()
      return self.mVariableDict
   
   def parse(self, filename):
      lines = open(filename).readlines()
      vars = {}
      locals = {}
      for line in lines:
       line = line.strip()
       if not line:
         continue
       elif ':' in line: # exported variable
         name, val = line.split(':')
         val = val.strip()
         if '$' in val:
           try:
             val = Template(val).substitute(locals)
           except ValueError:
             raise ValueError("Error in variable substitution!")
         vars[name] = val
       elif '=' in line: # local variable
         name, val = line.split('=')
         if '$' in val:
           try:
             val = Template(val).substitute(locals)
           except ValueError:
             raise ValueError("Error in variable substitution!")
         locals[name] = val
      return vars


class OptionsEvaluator:
   
   def __init__(self):
      self.mOptParser = self.GetOptionParser()
      (self.mOptions, self.mArgs) = self.mOptParser.parse_args()
      if self.mOptions.version:
         print "%s.%s.%s" % GetFlagpollVersion()
         sys.exit(0)
      if len(self.mArgs) < 1:
         self.mOptParser.print_help()
         sys.exit(1)
      self.mPkgDB = PkgDB()

   def evaluateArgs(self):

      if self.mOptions.debug:
         print self.mPkgDB.getInfo(self.mArgs[0])
         print "Ran with extra args: " + str(self.mArgs)

      if self.mOptions.variable:
         print self.mPkgDB.getVariable(self.mArgs[0], self.mOptions.variable)

      if self.mOptions.modversion:
         print self.mPkgDB.getVariable(self.mArgs[0], "Version")
         
      if self.mOptions.libs:
         print self.mPkgDB.getVariableAndDeps(self.mArgs[0], "Libs")

      if self.mOptions.static:
         print self.mPkgDB.getVariable(self.mArgs[0], "Static")

      if self.mOptions.cflags:
         print self.mPkgDB.getVariableAndDeps(self.mArgs[0], "Cflags")

#      if not self.mOptions.list_all:
#        print self.mPkgDB.getPkgList

#      if not self.mOptions.exists:
#         print self.mPkgDB.checkExistence(self.mArgs[0])


   def GetOptionParser(self):
      parser = OptionParser()
      parser.add_option("--modversion", action="store_true", dest="modversion", help="output version for package")
      parser.add_option("--version", action="store_true", dest="version", help="output version of pkg-config")
      parser.add_option("--libs", action="store_true", dest="libs", help="output all linker flags")
      parser.add_option("--static", action="store_true", dest="static", help="output linker flags for static linking")
      parser.add_option("--short-errors", action="store_true", dest="short_errors", help="print short errors")
      parser.add_option("--libs-only-l", action="store_true", dest="libs_only_l", help="output -l flags")
      parser.add_option("--libs-only-other", action="store_true", dest="libs_only_other", help="output other libs (e.g. -pthread)")
      parser.add_option("--libs-only-L", action="store_true", dest="libs_only_L", help="output -L flags")
      parser.add_option("--cflags", action="store_true", dest="cflags", help="output all pre-processor and compiler flags")
      parser.add_option("--cflags-only-I", action="store_true", dest="cflags_only_I", help="output -I flags")
      parser.add_option("--cflags-only-other ", action="store_true", dest="cflags_only_other", help="output cflags not covered by the cflags-only-I option")
      parser.add_option("--exists", action="store_true", dest="exists", help="return 0 if the module(s) exist")
      parser.add_option("--list-all", action="store_true", dest="list_all", help="list all known packages")
      parser.add_option("--debug", action="store_true", dest="debug", help="show verbose debug information")
      parser.add_option("--print-errors", action="store_true", dest="print_errors", help="show verbose information about missing or conflicting packages")
      parser.add_option("--silence-errors", action="store_true", dest="silence_errors", help="show no information about missing or conflicting packages")
      parser.add_option("--uninstalled", action="store_true", dest="uninstalled", help="return 0 if the uninstalled version of one or more module(s) or their dependencies will be used")
      parser.add_option("--errors-to-stdout", action="store_true", dest="errors_to_stdout", help="print errors from --print-errors to stdout not stderr")
      parser.add_option("--print-provides", action="store_true", dest="print_provides", help="print which packages the package provides")
      parser.add_option("--print-requires", action="store_true", dest="print_requires", help="print which packages the package requires")
      parser.add_option("--atleast-version", dest="atleast_version", help="return 0 if the module is at least version VERSION")
      parser.add_option("--exact-version", dest="exact_version", help="return 0 if the module is exactly version VERSION")
      parser.add_option("--max-version", dest="max_version", help="return 0 if the module is at no newer than version VERSION")
      parser.add_option("--atleast-pkgconfig-version=VERSION", dest="atleast_pkgconfig_version", help="require given version of pkg-config")
      parser.add_option("--variable", dest="variable", help="get the value of a variable")
      parser.add_option("--define-variable", dest="define_variable", help="set the value of a variable")
      return parser


# GO!
my_dep_system = DepResolutionSystem()
opt_evaluator = OptionsEvaluator()
opt_evaluator.evaluateArgs()
sys.exit(0)
