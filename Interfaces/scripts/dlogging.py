"""
  Retrieve logging information for a DIRAC job
"""

import DIRAC
from DIRAC.Core.Base import Script

class Params:
  def __init__ ( self ):
    self.fmt = "pretty"

  def setFmt( self, arg = None ):
    self.fmt = arg.lower()

  def getFmt( self ):
    return self.fmt

params = Params()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )
Script.registerSwitch( "f:", "Fmt=", "display format (pretty, csv, json)", params.setFmt )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Core.DISET.RPCClient import RPCClient
from COMDIRAC.Interfaces.Utilities.DCommands import ArrayFormatter

exitCode = 0

jobs = map( int, args )

monitoring = RPCClient( 'WorkloadManagement/JobMonitoring' )
af = ArrayFormatter( params.getFmt() )
headers = ["Status", "MinorStatus", "ApplicationStatus", "Time", "Source"]
errors = []
for job in jobs:
  result = monitoring.getJobLoggingInfo( job )
  if result['OK']:
    print af.listFormat( result['Value'], headers, sort = headers.index( "Time" ) )
  else:
    errors.append( result["Message"] )
    exitCode = 2

for error in errors:
  print "ERROR: %s" % error

DIRAC.exit( exitCode )

