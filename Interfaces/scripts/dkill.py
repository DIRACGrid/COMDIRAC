#!/usr/bin/env python
"""
  Kill or delete DIRAC job
"""
__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script
#
class Params:
  def __init__ ( self ):
    self.delete = False

  def setDelete( self, arg = None ):
    self.delete = True

  def getDelete( self ):
    return self.delete

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

params = Params()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID: a DIRAC job identifier', ] ) )
Script.registerSwitch( "D", "delete", "delete job", params.setDelete )
Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

exitCode = 0

from DIRAC.WorkloadManagementSystem.Client.WMSClient import WMSClient

wmsClient = WMSClient()

jobs = args

errors = []
for job in jobs:
  result = None
  if params.delete:
    result = wmsClient.deleteJob( job )
  else:
    result = wmsClient.killJob( job )
  if not result['OK']:
    errors.append( result['Message'] )
    exitCode = 2
  elif params.getVerbose():
    action = "killed"
    if params.getDelete(): action = "deleted"
    print "%s job %s" % ( action, job )

for error in errors:
  print "ERROR: %s" % error

DIRAC.exit( exitCode )
