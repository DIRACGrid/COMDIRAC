#!/usr/bin/env python

"""
  Retrieve status of DIRAC jobs
"""
__RCSID__ = "$Id$"

import os

import json

import DIRAC
from DIRAC import S_OK, S_ERROR
from DIRAC import exit as DIRACExit
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.Time import toString, date, day
from DIRAC.Core.DISET.RPCClient import RPCClient

from COMDIRAC.Interfaces.Utilities.DCommands import ArrayFormatter

# TODO: how to import job states from JobDB in client installation (lacks MySQLdb module)?
# from DIRAC.WorkloadManagementSystem.DB.JobDB import JOB_STATES, JOB_FINAL_STATES
JOB_STATES = ['Received', 'Checking', 'Staging', 'Waiting', 'Matched',
              'Running', 'Stalled', 'Done', 'Completed', 'Failed']
JOB_FINAL_STATES = ['Done', 'Completed', 'Failed']

def selectJobs( owner, date, jobGroup, jobName ):
  conditions = {'Owner' : owner}
  if jobGroup: conditions["JobGroup"] = jobGroup
  if jobName: conditions["JobName"] = jobName

  monitoring = RPCClient( 'WorkloadManagement/JobMonitoring' )
  result = monitoring.getJobs( conditions, date )

  return result

def getJobSummary( jobs ):
  if not jobs: return S_OK( {} )
  monitoring = RPCClient( 'WorkloadManagement/JobMonitoring' )
  result = monitoring.getJobsSummary( jobs )
  try:
    jobSummary = eval( result['Value'] )
  except:
    return S_ERROR( 'Problem while converting result from job monitoring' )
  return S_OK( jobSummary )

# to consider: "JobType", "ApplicationStatus", "StartExecTime", "EndExecTime",
# "CPUTime"
DEFAULT_DISPLAY_COLUMNS = [
  "Owner", "JobName", "OwnerGroup", "JobGroup", "Site", "Status", "MinorStatus", "SubmissionTime",
]

from COMDIRAC.Interfaces import DSession

class Params:
  def __init__ ( self, session ):
    self.__session = session
    self.user = None
    self.status = map( lambda e: e.lower(), set( JOB_STATES ) - set( JOB_FINAL_STATES ) )
    self.fmt = "pretty"
    self.jobDate = 10
    self.fields = DEFAULT_DISPLAY_COLUMNS
    customFields = session.getEnv( "dstat_fields", "" )['Value']
    if customFields:
      self.fields = customFields.split( ',' )
    self.jobGroup = None
    self.jobName = None

  def setUser( self, arg = None ):
    self.user = arg

  def getUser( self ):
    return self.user

  def setStatus( self, arg = None ):
    self.status = arg.lower().split( "," )

  def setStatusAll( self, arg = None ):
    self.status = map( lambda e: e.lower(), JOB_STATES )

  def getStatus( self ):
    return self.status

  def setFmt( self, arg = None ):
    self.fmt = arg.lower()

  def getFmt( self ):
    return self.fmt

  def setJobDate( self, arg = None ):
    self.jobDate = int( arg )

  def getJobDate( self ):
    return self.jobDate

  def setFields( self, arg = None ):
    self.fields = arg.split( "," )

  def getFields( self ):
    return self.fields

  def setJobGroup( self, arg = None ):
    self.jobGroup = arg

  def getJobGroup( self ):
    return self.jobGroup

  def setJobName( self, arg = None ):
    self.jobName = arg

  def getJobName( self ):
    return self.jobName

session = DSession()
params = Params( session )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ' % Script.scriptName,
                                     'Arguments:', ] ) )
Script.registerSwitch( "u:", "User=", "job owner", params.setUser )
Script.registerSwitch( "", "Status=", "select job by status", params.setStatus )
Script.registerSwitch( "a", "StatusAll", "display jobs of any status", params.setStatusAll )
Script.registerSwitch( "", "JobGroup=", "select job by job group", params.setJobGroup )
Script.registerSwitch( "", "JobName=", "select job by job name", params.setJobName )
Script.registerSwitch( "", "Fmt=", "display format (pretty, csv, json)", params.setFmt )
Script.registerSwitch( "", "JobDate=", "age of jobs to display", params.setJobDate )
Script.registerSwitch( "", "Fields=", "display list of fields", params.setFields )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

exitCode = 0

# time interval
jobDate = toString( date() - params.getJobDate() * day )

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

result = selectJobs( owner = userName, date = jobDate, jobGroup = params.getJobGroup(),
                     jobName = params.getJobName() )
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

af = ArrayFormatter( params.getFmt() )

# filter on job statuses
summaries = {}
statuses = params.getStatus()
if "all" in statuses:
  summaries = result['Value']
else:
  for j, s in result['Value'].items():
    if s["Status"].lower() in statuses:
      summaries[j] = s

for s in summaries.values():
  s["JobID"] = int( s["JobID"] )
print af.dictFormat( summaries, ["JobID"] + params.getFields(), sort = "JobID" )

DIRAC.exit( exitCode )
