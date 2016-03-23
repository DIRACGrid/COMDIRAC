"""
  Retrieve output sandbox for a DIRAC job
"""

import DIRAC
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Base import Script

import os

class Params:
  def __init__ ( self ):
    self.outputDir = None
    self.outputData = False
    self.outputSandbox = False
    self.verbose = False
    self.noJobDir = False
    self.jobGroup = []

  def setOutputDir( self, arg = None ):
    self.outputDir = arg

  def getOutputDir( self ):
    return self.outputDir

  def setOutputData( self, arg = None ):
    self.outputData = True

  def getOutputData( self ):
    return self.outputData

  def setOutputSandbox( self, arg = None ):
    self.outputSandbox = True

  def getOutputSandbox( self ):
    return self.outputSandbox

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

  def setNoJobDir( self, arg = None ):
    self.noJobDir = True

  def getNoJobDir( self ):
    return self.noJobDir

  def setJobGroup( self, arg = None ):
    if arg:
      self.jobGroup.append( arg )

  def getJobGroup( self ):
    return self.jobGroup

params = Params( )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )

Script.registerSwitch( "D:", "OutputDir=", "destination directory", params.setOutputDir )
Script.registerSwitch( "", "Data", "donwload output data instead of output sandbox", params.setOutputData )
Script.registerSwitch( "", "Sandbox", "donwload output sandbox, even if data was required", params.setOutputSandbox )
Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )
Script.registerSwitch( "n", "NoJobDir", "do not create job directory", params.setNoJobDir )
Script.registerSwitch( "g:", "JobGroup=", "Get output for jobs in the given group", params.setJobGroup )

configCache = ConfigCache()
Script.parseCommandLine( ignoreErrors = True )
configCache.cacheConfig()
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.Dirac  import Dirac
from DIRAC.Core.Utilities.Time import toString, date, day

dirac = Dirac()
exitCode = 0

for jobGroup in params.getJobGroup():
  jobDate = toString( date() - 30 * day )

  # Choose jobs in final state, no more than 30 days old
  for s in ['Done', 'Failed']:
    result = dirac.selectJobs( jobGroup = jobGroup, date = jobDate, status = s )
    if not result['OK']:
      if not "No jobs selected" in result['Message']:
        print "Error:", result['Message']
        exitCode = 2
    else:
      args += result['Value']

jobs = []

outputDir = params.getOutputDir() or os.path.curdir

for arg in args:
  if os.path.isdir( os.path.join( outputDir, arg ) ) and not params.getNoJobDir():
    print "Output for job %s already retrieved, remove the output directory to redownload" % arg
  else:
    jobs.append( arg )


if jobs:
  if not os.path.isdir( outputDir ):
    os.makedirs( outputDir )

  errors = []
  inputs = {}
  for job in jobs:
    if not params.getNoJobDir():
      destinationDir = os.path.join( outputDir, job )
    else:
      destinationDir = outputDir
    inputs[job] = {"destinationDir" : destinationDir}

    if params.getOutputSandbox() or not params.getOutputData():
      try:
        result = dirac.getOutputSandbox( job, outputDir = outputDir, noJobDir = params.getNoJobDir() )
      except TypeError:
        errors.append( "dirac.getOutputSandbox doesn't accept \"noJobDir\" argument. Will create per-job directories." )
        result = dirac.getOutputSandbox( job, outputDir = outputDir )
      if result['OK']:
        inputs[job]["osb"] = destinationDir
      else:
        errors.append( result["Message"] )
        exitCode = 2

    if params.getOutputData():
      result = dirac.getJobOutputData( job, destinationDir = destinationDir )
      if result['OK']:
        inputs[job]["data"] = result["Value"]
      else:
        errors.append( result["Message"] )
        exitCode = 2

  for error in errors:
    print "ERROR: %s" % error

  if params.getVerbose():
    for j, d in inputs.items():
      if "osb" in d: print "%s: OutputSandbox" % j, d["osb"]
      if "data" in d: print "%s: OutputData" % j, d["data"]

DIRAC.exit( exitCode )

