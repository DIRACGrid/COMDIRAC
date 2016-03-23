#! /usr/bin/env python

"""
  Submit jobs to DIRAC WMS

  Default JDL can be configured from session in the "JDL" option
"""

import os.path, sys
import re
import tempfile
from types import IntType

from DIRAC import S_OK
from DIRAC import exit as DIRACexit
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Base import Script

def parseScriptLinesJDLDirectives( lines ):
  ret = {}

  for l in lines:
    if l.startswith( '#JDL ' ):
      c = l[5:]
      d, v = c.split( '=', 1 )
      ret[d.strip()] = v.strip()
  return ret

def parseScriptJDLDirectives( fn ):
  f = open( fn, 'r' )
  lines = f.readlines()
  f.close()

  return parseScriptLinesJDLDirectives( lines )

def classAdAppendToInputSandbox( classAd, f ):
  classAdAppendToSandbox( classAd, f, "InputSandbox" )

def classAdAppendToOutputSandbox( classAd, f ):
  classAdAppendToSandbox( classAd, f, "OutputSandbox" )

def classAdAppendToSandbox( classAd, f, sbName ):
  sb = []
  if classAd.isAttributeList( sbName ):
    sb = classAd.getListFromExpression( sbName )
  sb.append ( f )
  classAdJob.insertAttributeVectorString( sbName, sb )

class Params:
  def __init__ ( self ):
    self.__session = None
    self.attribs = {}
    self.jdl = None
    self.parametric = None
    self.forceExecUpload = False
    self.verbose = False
    self.inputData = ''

  def setSession( self, session ):
    self.__session = session
    if self.inputData:
      self.attribs["InputData"] = self.pathListArg( self.inputData )

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

  def getDefaultJDL( self ):
    if not self.__session:
      JDL = ""
    else:  
      JDL = self.__session.getJDL()

    if JDL == "":
      # overall default JDL
      JDL = "[OutputSandbox = {\"std.out\",\"std.err\"};]"

    return JDL

  def setJDL( self, arg = None ):
    if os.path.isfile( arg ):
      f = open( arg, 'r' )
      arg = f.read()
      f.close()

    self.jdl = arg
    return S_OK()

  def getJDL( self ):
    if self.jdl:
      return self.jdl
    else:
      return self.getDefaultJDL()

  def setVerbose( self, arg = None ):
    self.verbose = True
    return S_OK()

  def getVerbose( self ):
    return self.verbose

  def setForceExecUpload( self, arg = None ):
    self.forceExecUpload = True
    return S_OK()
  def getForceExecUpload( self, arg = None ):
    return self.forceExecUpload

  def setName( self, arg = None ):
    self.attribs["JobName"] = arg
    return S_OK()
  def getName( self ):
    return self.attribs["JobName"]

  def setStdError( self, arg = None ):
    self.attribs["StdError"] = arg
    return S_OK()
  def getStdError( self ):
    return self.attribs["StdError"]

  def setStdOutput( self, arg = None ):
    self.attribs["StdOutput"] = arg
    return S_OK()
  def getStdOutput( self ):
    return self.attribs["StdOutput"]

  def setOutputSandbox( self, arg = None ):
    self.attribs["OutputSandbox"] = self.listArg( arg )
    return S_OK()
  def getOutputSandbox( self ):
    return self.attribs["OutputSandbox"]

  def setInputSandbox( self, arg = None ):
    self.attribs["InputSandbox"] = self.listArg( arg )
    return S_OK()
  def getInputSandbox( self ):
    return self.attribs["InputSandbox"]

  def setInputData( self, arg = None ):
    self.inputData = arg
    return S_OK()
  def getInputData( self ):
    return self.attribs.get( "InputData", [] )

  def setOutputData( self, arg = None ):
    self.attribs["OutputData"] = self.listArg( arg )
    return S_OK()
  def getOutputData( self ):
    return self.attribs["OutputData"]

  def setOutputPath( self, arg = None ):
    self.attribs["OutputPath"] = arg
    return S_OK()
  def getOutputPath( self ):
    return self.attribs["OutputPath"]

  def setOutputSE( self, arg = None ):
    self.attribs["OutputSE"] = arg
    return S_OK()
  def getOutputSE( self ):
    return self.attribs["OutputSE"]

  def setCPUTime( self, arg = None ):
    self.attribs["CPUTime"] = arg
    return S_OK()
  def getCPUTime( self ):
    return self.attribs["CPUTime"]

  def setSite( self, arg = None ):
    self.attribs["Site"] = self.listArg( arg )
    return S_OK()
  def getSite( self ):
    return self.attribs["Site"]

  def setBannedSite( self, arg = None ):
    self.attribs["BannedSite"] = self.listArg( arg )
    return S_OK()
  def getBannedSite( self ):
    return self.attribs["BannedSite"]

  def setPlatform( self, arg = None ):
    self.attribs["Platform"] = self.listArg( arg )
    return S_OK()
  def getPlatform( self ):
    return self.attribs["Platform"]

  def setPriority( self, arg = None ):
    self.attribs["Priority"] = arg
    return S_OK()
  def getPriority( self ):
    return self.attribs["Priority"]

  def setJobGroup( self, arg = None ):
    self.attribs["JobGroup"] = arg
    return S_OK()
  def getJobGroup( self ):
    return self.attribs["JobGroup"]

  def setParametric( self, arg = None ):
    self.parametric = arg.split( ',' )
    return S_OK()
  def getParametric( self ):
    return self.parametric

  def modifyClassAd( self, classAd ):
    classAd.contents.update( self.attribs )

  def parameterizeClassAd( self, classAd ):
    def classAdClone( classAd ):
      return ClassAd( classAd.asJDL() )

    if not self.parametric: return [classAd]

    float_pat = '[-+]?(((\d*\.)?\d+)|(\d+\.))([eE][-+]\d+)?'
    loop_re = re.compile( "^(?P<start>%(fp)s):(?P<stop>%(fp)s)(:(?P<step>%(fp)s))?$" % {'fp' : float_pat} )
    parameters = []
    loops = []
    for param in self.parametric:
      m = loop_re.match( param )
      if m:
        loop = m.groupdict()
        try:
          start = int( loop["start"] )
          stop = int( loop["stop"] )
        except ValueError:
          start = float( loop["start"] )
          stop = float( loop["stop"] )
        step = 1
        if "step" in loop and loop["step"]:
          try:
            step = int( loop["step"] )
          except ValueError:
            step = float( loop["step"] )
        loops.append( ( start, stop, step ) )
      else:
        parameters.append( param )

    ret = []
    if parameters:
      new = classAdClone( classAd )
      new.insertAttributeVectorString( "Parameters", parameters )
      ret.append( new )

    for start, stop, step in loops:
      new = classAdClone( classAd )
      number = int( ( stop - start ) / step ) + 1
      new.insertAttributeString( "ParameterStart", str( start ) )
      new.insertAttributeInt( "Parameters", number )
      new.insertAttributeString( "ParameterStep", str( step ) )
      ret.append( new )

    return ret

params = Params()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] [executable [--] [arguments...]]' % Script.scriptName,
                                     'Arguments:',
                                     '  executable: command to be run inside the job. ',
                                     '              If a relative path, local file will be included in InputSandbox',
                                     '              If no executable is given and JDL (provided or default) doesn\'t contain one,',
                                     '              standard input will be read for executable contents',
                                     '  arguments: arguments to pass to executable',
                                     '             if some arguments are to begin with a dash \'-\', prepend \'--\' before them', ] ) )

Script.registerSwitch( "J:", "JDL=", "JDL file or inline", params.setJDL )
Script.registerSwitch( "N:", "JobName=", "job name", params.setName )
Script.registerSwitch( "E:", "StdError=", "job standard error file", params.setStdError )
Script.registerSwitch( "O:", "StdOutput=", "job standard output file", params.setStdOutput )
Script.registerSwitch( "", "OutputSandbox=", "job output sandbox", params.setOutputSandbox )
Script.registerSwitch( "", "InputSandbox=", "job input sandbox", params.setInputSandbox )
Script.registerSwitch( "", "OutputData=", "job output data", params.setOutputData )
Script.registerSwitch( "", "InputData=", "job input data", params.setInputData )
Script.registerSwitch( "", "OutputPath=", "job output data path prefix", params.setOutputPath )
Script.registerSwitch( "", "OutputSE=", "job output data SE", params.setOutputSE )
Script.registerSwitch( "", "CPUTime=", "job CPU time limit (in seconds)", params.setCPUTime )
Script.registerSwitch( "", "Site=", "job Site list", params.setSite )
Script.registerSwitch( "", "BannedSite=", "job Site exclusion list", params.setBannedSite )
Script.registerSwitch( "", "Platform=", "job Platform list", params.setPlatform )
Script.registerSwitch( "", "Priority=", "job priority", params.setPriority )
Script.registerSwitch( "", "JobGroup=", "job JobGroup", params.setJobGroup )
Script.registerSwitch( "", "Parametric=", "comma separated list or named parameters or integer loops (in the form<start>:<stop>[:<step>])",
                       params.setParametric )
Script.registerSwitch( "", "ForceExecUpload", "Force upload of executable with InputSandbox",
                       params.setForceExecUpload )

Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )


configCache = ConfigCache()
Script.parseCommandLine( ignoreErrors = True )
configCache.cacheConfig()

args = Script.getPositionalArgs()

cmd = None
cmdArgs = []
if len( args ) >= 1:
  cmd = args[0]
  cmdArgs = args[1:] 

from DIRAC.Core.Utilities.ClassAd.ClassAdLight import ClassAd

from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import pathFromArgument

from DIRAC.Interfaces.API.Dirac import Dirac

session = DSession()
params.setSession( session )

dirac = Dirac()
exitCode = 0
errorList = []

classAdJob = ClassAd( params.getJDL() )

params.modifyClassAd( classAdJob )

# retrieve JDL provided Executable if present and user did not provide one
jdlExecutable = classAdJob.getAttributeString( "Executable" )
if jdlExecutable and not cmd:
  cmd = jdlExecutable

tempFiles = []
if cmd is None:
  # get executable script from stdin
  if sys.stdin.isatty():
    print "\nThe executable is not given"
    print "Type in the executable script lines, finish with ^D"
    print "or exit job submission with ^C\n"

  lines = sys.stdin.readlines()

  # Manage JDL directives inserted in cmd
  jdlDirectives = parseScriptLinesJDLDirectives( lines )
  classAdJob.contents.update( jdlDirectives )
  # re-apply parameters options to take priority over script JDL directives
  params.modifyClassAd( classAdJob )


  f = tempfile.NamedTemporaryFile( delete = False )
  fn = f.name
  for l in lines: f.write( l )
  f.close()
  tempFiles.append( fn )

  classAdJob.insertAttributeString( "Executable", os.path.basename( fn ) )

  classAdAppendToInputSandbox( classAdJob, fn )

  if not classAdJob.lookupAttribute( "JobName" ):
    classAdJob.insertAttributeString( "JobName", "STDIN" )

else:
  # Manage JDL directives inserted in cmd
  jdlDirectives = parseScriptJDLDirectives( cmd )
  classAdJob.contents.update( jdlDirectives )
  # re-apply parameters options to take priority over script JDL directives
  params.modifyClassAd( classAdJob )

  # Executable name provided
  if params.getForceExecUpload() and cmd.startswith( "/" ):
    # job will use uploaded executable (relative path)
    classAdJob.insertAttributeString( "Executable", os.path.basename( cmd ) )
  else:
    classAdJob.insertAttributeString( "Executable", cmd )

  uploadExec = params.getForceExecUpload() or not cmd.startswith( "/" )
  if uploadExec:
    if not os.path.isfile( cmd ):
      print "ERROR: executable file \"%s\" not found" % cmd
      DIRACexit( 2 )

    classAdAppendToInputSandbox( classAdJob, cmd )

    # set job name based on script file name
    if not classAdJob.lookupAttribute( "JobName" ):
      classAdJob.insertAttributeString( "JobName", cmd )

  if cmdArgs:
    classAdJob.insertAttributeString( "Arguments", " ".join( cmdArgs ) )
    
classAdJobs = params.parameterizeClassAd( classAdJob )

if params.getVerbose():
  print "JDL:"
  for p in params.parameterizeClassAd( classAdJob ):
    print p.asJDL()

jobIDs = []



for classAdJob in classAdJobs:
  jdlString = classAdJob.asJDL()  
  result = dirac.submit( jdlString )
  if result['OK']:
    if type( result['Value'] ) == IntType:
      jobIDs.append( result['Value'] )
    else:
      jobIDs += result['Value']
  else:
    errorList.append( ( jdlString, result['Message'] ) )
    exitCode = 2

if jobIDs:
  if params.getVerbose():
    print "JobID:",
  print ','.join( map ( str, jobIDs ) )

# remove temporary generated files, if any
for f in tempFiles:
  try:
    os.unlink( f )
  except Exception, e:
    errorList.append( str( e ) )

for error in errorList:
  print "ERROR %s: %s" % error

DIRACexit( exitCode )
