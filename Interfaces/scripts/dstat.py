#!/usr/bin/env python

"""
  Retrieve status of DIRAC jobs
"""
__RCSID__ = "$Id$"

import os
import DIRAC
from DIRAC import S_OK, S_ERROR
from DIRAC import exit as DIRACExit
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.Time import toString, date, day
from DIRAC.Core.DISET.RPCClient import RPCClient
# TODO: how to import job states from JobDB in client installation (lacks MySQLdb module)?
# from DIRAC.WorkloadManagementSystem.DB.JobDB import JOB_STATES, JOB_FINAL_STATES
JOB_STATES = ['Received', 'Checking', 'Staging', 'Waiting', 'Matched',
              'Running', 'Stalled', 'Done', 'Completed', 'Failed']
JOB_FINAL_STATES = ['Done', 'Completed', 'Failed']

def getJobSummary( jobs ):
  monitoring = RPCClient( 'WorkloadManagement/JobMonitoring' )
  result = monitoring.getJobsSummary( jobs )
  try:
    jobSummary = eval( result['Value'] )
  except:
    return S_ERROR( 'Problem while converting result from job monitoring' )
  return S_OK( jobSummary )

# to consider: "JobType", "ApplicationStatus", "OwnerGroup", "StartExecTime", "EndExecTime",
# "CPUTime"
DEFAULT_DISPLAY_COLUMNS = [
  "Owner", "JobName", "JobGroup", "Site", "Status", "MinorStatus", "SubmissionTime",
]
def formatCSV( summaries, columns = DEFAULT_DISPLAY_COLUMNS ):
  ret = "JobID,"
  for c in columns:
    ret += c + ","
  ret += "\n"


  for j, s in summaries.items():
    ret += str( j ) + ","
    for c in columns:
      ret += s[c] + ","
    ret += "\n"

  return ret

from COMDIRAC.Interfaces import DSession

class Params:
  def __init__ ( self, session ):
    self.__session = session
    self.user = None
    self.status = map( lambda e: e.lower(), set( JOB_STATES ) - set( JOB_FINAL_STATES ) )

  def setUser( self, arg = None ):
    self.user = arg

  def getUser( self ):
    return self.user

  def setStatus( self, arg = None ):
    self.status = arg.lower().split( "," )

  def getStatus( self ):
    return self.status

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ' % Script.scriptName,
                                     'Arguments:', ] ) )
Script.registerSwitch( "u:", "User=", "job owner", params.setUser )
Script.registerSwitch( "", "Status=", "statuses of jobs to display", params.setStatus )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.Dirac  import Dirac
dirac = Dirac()
exitCode = 0

jobDate = toString( date() - 30 * day )

# job owner
userName = params.getUser()
if userName is None:
  Script.enableCS()
  result = session.getUserName()
  if result["OK"]:
    userName = result["Value"]
elif userName == "*" or userName.lower() == "__all__":
  # jobs from all users
  userName = None

result = dirac.selectJobs( owner = userName, date = jobDate )
if not result['OK']:
  print "Error:", result['Message']
  DIRACExit( -1 )

jobs = result['Value']

try:
  jobs = [ int( job ) for job in jobs ]
except Exception, x:
  print 'Expected integer for jobID'
  exitCode = 2
  DIRAC.exit( exitCode )

result = getJobSummary( jobs )
if not result['OK']:
  print "ERROR: %s" % result['Message']
  DIRAC.exit( 2 )

summaries = result['Value']

print formatCSV( summaries )

DIRAC.exit( exitCode )
