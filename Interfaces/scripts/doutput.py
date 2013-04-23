"""
  Retrieve output sandbox for a DIRAC job
"""

import DIRAC
from DIRAC.Core.Base import Script

import os, shutil, datetime

from COMDIRAC.Interfaces import DSession

class Params:
  def __init__ ( self, session ):
    self.__session = session
    self.outputDir = None
    self.outputData = False
    self.verbose = False

  def setOutputDir( self, arg = None ):
    self.outputDir = arg

  def getOutputDir( self ):
    return self.outputDir

  def setOutputData( self, arg = None ):
    self.outputData = True

  def getOutputData( self ):
    return self.outputData

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
Script.registerSwitch( "", "Data", "retrieve output data", params.setOutputData )
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
    print "Output for job %s already retrieved, remove the output directory to redownload" % arg
  else:
    jobs.append( arg )

if jobs:
  if not os.path.isdir( outputDir ):
    os.makedirs( outputDir )

  errors = []
  outputs = {}
  for job in jobs:
    destinationDir = os.path.join( outputDir, job )
    outputs[job] = {"destinationDir" : destinationDir}
    result = dirac.getOutputSandbox( job, outputDir = outputDir )
    if result['OK']:
      outputs[job]["osb"] = destinationDir
    else:
      errors.append( result["Message"] )
      exitCode = 2
    if params.getOutputData():
      result = dirac.getJobOutputData( job, destinationDir = destinationDir )
      if result['OK']:
        outputs[job]["data"] = result["Value"]
      else:
        errors.append( result["Message"] )
        exitCode = 2

  for error in errors:
    print "ERROR: %s" % error

  if params.getVerbose():
    for j, d in outputs.items():
      if "osb" in d: print "%s: OutputSandbox" % j, d["osb"]
      if "data" in d: print "%s: OutputData" % j, d["data"]

DIRAC.exit( exitCode )

