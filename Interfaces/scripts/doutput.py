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

  def setOutputDir( self, arg = None ):
    self.outputDir = arg

  def getOutputDir( self ):
    return self.outputDir

  def setOutputData( self, arg = None ):
    self.outputData = True

  def getOutputData( self ):
    return self.outputData

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )

Script.registerSwitch( "D:", "OutputDir=", "destination directory", params.setOutputDir )
Script.registerSwitch( "", "Data", "retrieve output data", params.setOutputData )

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
  for job in jobs:
    result = dirac.getOutputSandbox( job, outputDir = outputDir )
    if not result['OK']:
      errors.append( result["Message"] )
      exitCode = 2
    if params.getOutputData():
      result = dirac.getJobOutputData( job, destinationDir = os.path.join( outputDir, job ) )
      if not result['OK']:
        errors.append( result["Message"] )
        exitCode = 2

  for error in errors:
    print "ERROR: %s" % error

DIRAC.exit( exitCode )

