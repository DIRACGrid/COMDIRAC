#! /usr/bin/env python

"""
  Submit jobs to DIRAC WMS

  Default JDL can be configured from session in the "JDL" option
"""

import os.path

import DIRAC
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.ClassAd.ClassAdLight import ClassAd

from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import pathFromArgument

def getDefaultJDL( session ):
  JDL = session.getJDL()

  if JDL == "":
    # overall default JDL
    JDL = "[OutputSandbox = {\"std.out\",\"std.err\"};]"

  return JDL

def classAdUpdate( toClassAd, fromClassAd ):
  toClassAd.contents.update( fromClassAd.contents )

class Params:
  def __init__ ( self, session ):
    self.__session = session
    self.attribs = {}
    self.verbose = False

  def listArg( self, arg ):
    if arg and not arg.startswith( "{" ):
      arg = "{" + arg + "}"
    return arg

  def pathListArg( self, arg ):
    if not arg: return arg

    arg = arg.strip( "{}" )
    args = arg.split( "," )

    pathlist = []
    for path in args:
      pathlist.append( pathFromArgument( self.__session, path ) )
    return "{" + ",".join( pathlist ) + "}"

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

  def setName( self, arg = None ):
    self.attribs["JobName"] = arg
  def getName( self ):
    return self.attribs["JobName"]

  def setStdError( self, arg = None ):
    self.attribs["StdError"] = arg
  def getStdError( self ):
    return self.attribs["StdError"]

  def setStdOutput( self, arg = None ):
    self.attribs["StdOutput"] = arg
  def getStdOutput( self ):
    return self.attribs["StdOutput"]

  def setOutputSandbox( self, arg = None ):
    self.attribs["OutputSandbox"] = self.listArg( arg )
  def getOutputSandbox( self ):
    return self.attribs["OutputSandbox"]

  def setInputSandbox( self, arg = None ):
    self.attribs["InputSandbox"] = self.listArg( arg )
  def getInputSandbox( self ):
    return self.attribs["InputSandbox"]

  def setInputData( self, arg = None ):
    self.attribs["InputData"] = self.pathListArg( arg )
  def getInputData( self ):
    return self.attribs["InputData"]

  def setOutputData( self, arg = None ):
    self.attribs["OutputData"] = self.listArg( arg )
  def getOutputData( self ):
    return self.attribs["OutputData"]

  def setOutputPath( self, arg = None ):
    self.attribs["OutputPath"] = arg
  def getOutputPath( self ):
    return self.attribs["OutputPath"]

  def setOutputSE( self, arg = None ):
    self.attribs["OutputSE"] = pathFromArgument( self.__session, arg )
  def getOutputSE( self ):
    return self.attribs["OutputSE"]

  def set( self, arg = None ):
    self.attribs[""] = arg
  def get( self ):
    return self.attribs[""]

  def modifyClassAd( self, classAd ):
    classAd.contents.update( self.attribs )

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] [executable [--] [arguments...]]' % Script.scriptName,
                                     'Arguments:',
                                     '  executable: command to be run inside the job. ',
                                     '              If a relative path, local file will be included in InputSandbox',
                                     '  arguments: arguments to pass to executable',
                                     '             if some arguments are to begin with a dash \'-\', prepend \'--\' before them', ] ) )

Script.registerSwitch( "N:", "name=", "job name", params.setName )
Script.registerSwitch( "E:", "StdError=", "job standard error file", params.setStdError )
Script.registerSwitch( "O:", "StdOutput=", "job standard output file", params.setStdOutput )
Script.registerSwitch( "", "OutputSandbox=", "job output sandbox", params.setOutputSandbox )
Script.registerSwitch( "", "InputSandbox=", "job input sandbox", params.setInputSandbox )
Script.registerSwitch( "", "OutputData=", "job output data", params.setOutputData )
Script.registerSwitch( "", "InputData=", "job input data", params.setInputData )
Script.registerSwitch( "", "OutputPath=", "job output data path prefix", params.setOutputPath )
Script.registerSwitch( "", "OutputSE=", "job output data SE", params.setOutputSE )
# Script.registerSwitch( ":", "=", "", params.set )

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

jdlString = getDefaultJDL( session )
classAdJob = ClassAd( jdlString )

params.modifyClassAd( classAdJob )

if cmd is not None:
  classAdJob.insertAttributeString( "Executable", cmd )
  if not cmd.startswith( "/" ) and os.path.isfile( cmd ):
    isb = []
    if classAdJob.isAttributeList( "Inputandbox" ):
      isb = classAdJob.getListFromExpression( "InputSandbox" )

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
