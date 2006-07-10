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

"""Makes a flagpole .fpc file from user input.

v0.9 coded by Jeff Groves"""
import os
import sys
import getopt

##String prompts for the input

varPrompt = """Variables (one 'var_name: var_definition' per line,""" + \
            """ empty line when done)"""
namePrompt = "Formal Name"
descriptionPrompt = "Description"
urlPrompt = "URL"
providesPrompt = "Look-Up Names (Provides)"
versionPrompt = "Version"
architecturePrompt = "Architecture"
requirePrompt = "Requires"
libPrompt = "Standard Linking Flags/Libs"
staticLibPrompt = "Static Linking Flags/Libs"
compileFlagsPrompt = "Compile/Include Flags" 
fileNamePrompt = "FPC File's Name"

def usage():
    """Prints a list of acceptable arguments for fpcmaker.py."""
    print """
Fpcmaker.py Options:
-n, --name= : Sets %s
-d, --description= : Sets %s
-u, --url= : Sets %s
-p, --provides= : Sets %s
-v, --version= : Sets %s
-a, --architecture= : Sets %s
-r, --requires= : Sets %s
-l, --libs= : Sets %s
-c, --cflags= : Sets %s
-s, --static= : Sets %s
-f, --file= : Sets %s  
""" %(namePrompt, descriptionPrompt, urlPrompt, providesPrompt,
      versionPrompt, architecturePrompt,
      requirePrompt, libPrompt, compileFlagsPrompt,
      staticLibPrompt, fileNamePrompt)
    return

def checkFileName(fileName):
    """Checks if the fpc file name's blank, contains slashes, or exists."""
    nameCleared = False
    writeFile = True
    confirms = ['y', 'Y', 'yes', 'Yes']
    ##Loops until the name clears or writing the file's aborted.
    while(not nameCleared and writeFile):
        ##If it's blank, give the option of aborting the program.
        if fileName == "":
            choice = raw_input("Do you want to abort writing the" +
                               " .fpc file? (Y/N): ")
            if choice not in confirms:
                fileName = raw_input("Please enter a different name for the" +
                                     " .fpc file: ")
            else:
                writeFile = False
        ##If it contains slashes, ask for another name.
        elif '/' in fileName or '\\' in fileName:
            print "I can't write to %s because it contains slashes."%(fileName)
            fileName = raw_input("Please enter a different name for the" +
                                 " .fpc file: ")
        ##If it already exists, ask if they want to overwrite.
        ##If not, ask for another name.
        elif os.path.exists(fileName):
            choice = raw_input("The file %s already exists." %(fileName) +
                               " Do you want to overwrite it? (Y/N): ")
            if choice not in confirms:
                fileName = raw_input("Please enter a different name for the" +
                                     " .fpc file: ")
            else:
                nameCleared = True
        else:
            nameCleared = True
    return [fileName, writeFile]

##Booleans for whether that argument was sent in the command line
varSet = False
providesSet = False
nameSet = False
descriptionSet = False
urlSet = False
architectureSet = False
versionSet = False
requiresSet = False
libsSet = False 
compileFlagsSet = False
staticLibSet = False
fileNameSet = False
##Get the options & arguments sent.
arguments = sys.argv[1:]
try:
    opts, args = getopt.getopt(arguments,
                               "p:n:u:d:a:r:v:l:c:s:f:",
                               ["provides=", "name=", "url=", "description=",
                                "architecture=", "requires=", "version=",
                                "libs=", "cflags=", "static=", "file="])
##Send them usage info if they enter a wrong argument
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-p', '--provides'):
        providesSet = True
        provides = arg
    elif opt in ('-n', '--name'):
        nameSet = True
        name = arg
    elif opt in ('-v', '--version'):
        versionSet = True
        version = arg
    elif opt in ('-u', '--url'):
        urlSet = True
        url = arg
    elif opt in ('-d', '--description'):
        descriptionSet = True
        description = arg
    elif opt in ('-a', '--architecture'):
        architectureSet = True
        architecture = arg
    elif opt in ('-r', '--requires'):
        requiresSet = True
        requires = arg
    elif opt in ('-l', '--libs'):
        libsSet = True
        libs = arg
    elif opt in ('-c', '--cflags'):
        compileFlagsSet = True
        compileFlags = arg
    elif opt in ('-s', '--static'):
        staticLibSet = True
        staticLib = arg
    elif opt in ('-f', '--file'):
        fileNameSet = True
        fileName = arg

##Grab any input not passed in the arguments from the user.
if not varSet:
    varLine = None
    variables = ""
    print "%s:" %(varPrompt)
    while(varLine != ""):
        varLine = raw_input("")
        variables = variables + "%s\n" %(varLine)
if not nameSet:
    name = raw_input("%s: " %(namePrompt))
if not descriptionSet:
    description = raw_input("%s: " %(descriptionPrompt))
if not urlSet:
    url = raw_input("%s: " %(urlPrompt))
if not versionSet:
    version = raw_input("%s: " %(versionPrompt))
if not providesSet:
    provides = raw_input("%s: " %(providesPrompt))
if not requiresSet:
    requires = raw_input("%s: " %(requirePrompt))
if not architectureSet:
    architecture = raw_input("%s: " %(architecturePrompt))
if not libsSet:
    libs = raw_input("%s: " %(libPrompt))
if not staticLibSet:
    staticLib = raw_input("%s: " %(staticLibPrompt))
if not compileFlagsSet:
    compileFlags = raw_input("%s: " %(compileFlagsPrompt))
if not fileNameSet:
    fileName = raw_input("%s: " %(fileNamePrompt))
##Check the file's name.
fileName, writeFile = checkFileName(fileName)

##If they chose not to overwrite, write the file.
if writeFile:
    fpc = open(fileName, 'w')
    fpc.write("%s" %(variables))
    fpc.write("Name= %s\n" %(name))
    fpc.write("Description= %s\n" %(description))
    fpc.write("URL= %s\n" %(url))
    fpc.write("Version= %s\n" %(version))
    fpc.write("Provides= %s\n" %(provides))
    fpc.write("Requires= %s\n" %(requires))
    fpc.write("Arch= %s\n" %(architecture))
    fpc.write("Libs= %s\n" %(libs))
    fpc.write("Libs.private= %s\n" %(staticLib))
    fpc.write("Cflags= %s\n" %(compileFlags))
    fpc.close()

##TESTER: Print the file out.
fpc = open(fileName, 'r') ##TESTER
print fpc.read()          ##TESTER
fpc.close                 ##TESTER
