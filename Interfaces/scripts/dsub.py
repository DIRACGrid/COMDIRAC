#!/usr/bin/env python

"""
  Submit jobs to DIRAC WMS

  Default JDL can be configured from session in the "JDL" option
"""

import os.path

import DIRAC
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.ClassAd.ClassAdLight import ClassAd
from COMDIRAC.Interfaces import DSession

def getDefaultJDL( session ):
  JDL = session.getJDL()

  if JDL == "":
    # overall default JDL
    JDL = "[OutputSandbox = {\"std.out\",\"std.err\"};]"

  return JDL

def classAdUpdate( toClassAd, fromClassAd ):
  toClassAd.contents.update( fromClassAd.contents )

class Params:
  def __init__ ( self ):
    self.name = None
    self.verbose = False

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

  def setName( self, arg = None ):
    self.name = arg

  def getName( self ):
    return self.name

  def modifyClassAd( self, classAd ):
    if self.name is not None:
      classAd.insertAttributeString( "JobName", self.name )

params = Params()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] [executable [--] [arguments...]]' % Script.scriptName,
                                     'Arguments:',
                                     '  executable: command to be run inside the job. ',
                                     '              If a relative path, local file will be included in InputSandbox',
                                     '  arguments: arguments to pass to executable',
                                     '             if some arguments are to begin with a dash \'-\', prepend \'--\' before them', ] ) )

Script.registerSwitch( "N:", "name=", "job name", params.setName )
Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

cmd = None
cmdArgs = []
if len( args ) >= 1:
  cmd = args[0]
  cmdArgs = args[1:]

from DIRAC.Interfaces.API.Dirac import Dirac
dirac = Dirac()
exitCode = 0
errorList = []

session = DSession()
jdlString = getDefaultJDL( session )
classAdJob = ClassAd( jdlString )

params.modifyClassAd( classAdJob )

if cmd is not None:
  classAdJob.insertAttributeString( "Executable", cmd )
  if not cmd.startswith( "/" ) and os.path.isfile( cmd ):
    isb = []
    if classAdJob.isAttributeList( "Inputandbox" ):
      isb = classAdJob.getListFromExpression( "InputSandbox" )
    print isb
    isb.append ( cmd )

    classAdJob.insertAttributeVectorString( "InputSandbox", isb )

  if cmdArgs:
    classAdJob.insertAttributeString( "Arguments", " ".join( cmdArgs ) )

if params.getVerbose():
  print "JDL:"
  print classAdJob.asJDL()
  print

# DIRAC.exit( exitCode )

jdlString = classAdJob.asJDL()
result = dirac.submit( jdlString )
if result['OK']:
  if params.getVerbose():
    print "JobID:",
  print '%s' % ( result['Value'] )
else:
  errorList.append( ( jdlString, result['Message'] ) )
  exitCode = 2

for error in errorList:
  print "ERROR %s: %s" % error

DIRAC.exit( exitCode )
