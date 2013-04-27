"""
  Retrieve input sandbox for a DIRAC job
"""

import DIRAC
from DIRAC.Core.Base import Script

import os
import pprint

from COMDIRAC.Interfaces import DSession

class Params:
  def __init__ ( self, session ):
    self.__session = session
    self.outputDir = None
    self.verbose = False
    self.downloadJDL = False

  def setOutputDir( self, arg = None ):
    self.outputDir = arg

  def getOutputDir( self ):
    return self.outputDir

  def setDownloadJDL( self, arg = None ):
    self.downloadJDL = True

  def getDownloadJDL( self ):
    return self.downloadJDL

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )

Script.registerSwitch( "D:", "OutputDir=", "destination directory", params.setOutputDir )
Script.registerSwitch( "j", "JDL", "also download job JDL", params.setDownloadJDL )
Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.Dirac  import Dirac

dirac = Dirac()
exitCode = 0

jobs = []

outputDir = params.getOutputDir() or os.path.curdir

for arg in args:
  if os.path.isdir( os.path.join( outputDir, arg ) ):
    print "Input for job %s already retrieved, remove the output directory to redownload" % arg
  else:
    jobs.append( arg )

if jobs:
  if not os.path.isdir( outputDir ):
    os.makedirs( outputDir )

  errors = []
  inputs = {}
  for job in jobs:
    destinationDir = os.path.join( outputDir, "InputSandbox%s" % job )
    inputs[job] = {"destinationDir" : destinationDir}
    result = dirac.getInputSandbox( job, outputDir = outputDir )
    if result['OK']:
      inputs[job]["isb"] = destinationDir
    else:
      errors.append( result["Message"] )
      exitCode = 2
    if params.getDownloadJDL():
      result = dirac.getJobJDL( job, printOutput = False )
      if result['OK']:
        jdl = pprint.pformat( result["Value"] )
        f = open ( os.path.join( destinationDir, "%s.jdl" % job ), 'w' )
        f.write( jdl )
        f.close()
        inputs[job]["jdl"] = jdl
      else:
        errors.append( result["Message"] )
        exitCode = 2

  for error in errors:
    print "ERROR: %s" % error

  if params.getVerbose():
    for j, d in inputs.items():
      if "isb" in d: print "%s: InputSandbox" % j, d["isb"]
      if "jdl" in d: print "%s: JDL" % j, d["jdl"]
DIRAC.exit( exitCode )

