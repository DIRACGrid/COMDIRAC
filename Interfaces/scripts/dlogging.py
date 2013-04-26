"""
  Retrieve logging information for a DIRAC job
"""

import DIRAC
from DIRAC.Core.Base import Script
from DIRAC.Core.DISET.RPCClient import RPCClient

import os, shutil, datetime

from COMDIRAC.Interfaces import DSession

def formatPretty( summaries, headers = ["Status", "MinorStatus", "ApplicationStatus", "Time", "Source"] ):
  headerWidths = {}
  for i, c in enumerate( headers ):
    headerWidths[i] = len( c )

  for s in summaries:
    for i, v in enumerate( s ):
      l = len ( str( v ) )
      if l > headerWidths[i]:
        headerWidths[i] = l

  ret = ""
  for i, header in enumerate( headers ):
    ret += "{field:^{width}} ".format( field = header, width = headerWidths[i] )
  ret += "\n"
  for i, header in enumerate( headers ):
    ret += "{field} ".format( field = "-" * headerWidths[i] )
  ret += "\n"

  for s in summaries:
    for i, header in enumerate( headers ):
      ret += "{field:^{width}} ".format( field = s[i], width = headerWidths[i] )
    ret += "\n"

  return ret

class Params:
  def __init__ ( self, session ):
    self.__session = session

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

exitCode = 0

jobs = map( int, args )

monitoring = RPCClient( 'WorkloadManagement/JobMonitoring' )
errors = []
for job in jobs:
  result = monitoring.getJobLoggingInfo( job )
  if result['OK']:
    print formatPretty( result['Value'] )
  else:
    errors.append( result["Message"] )
    exitCode = 2

for error in errors:
  print "ERROR: %s" % error

DIRAC.exit( exitCode )

