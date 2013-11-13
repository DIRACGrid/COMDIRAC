#!/usr/bin/env python

"""
Display information about the user jobs
"""

from COMDIRAC.Interfaces import critical
from DIRAC.Core.Base import Script
from DIRAC import exit as DIRACexit
from DIRAC import S_OK
from DIRAC.Core.Utilities.Time import toString, date, day

owner = None
def setOwner( option ):
  global owner
  owner = option
  return S_OK()

group = None
def setOwnerGroup( option ):
  global group
  group = option
  return S_OK()

status = None
def setStatus( option ):
  global status
  status = option
  return S_OK()

site = None
def setSite( option ):
  global site
  site = option
  return S_OK()

jobGroup = None
def setJobGroup( option ):
  global jobGroup
  jobGroup = option
  return S_OK()

date = toString( date() - 30*day )
def setDate( option ):
  global date
  date = option
  return S_OK()

verbose = False
def setVerbose( option ):
  global verbose
  verbose = True
  return S_OK()


Script.registerSwitch( "u:", "user=", "choose jobs of this user", setOwner )
Script.registerSwitch( "g:", "group=", "choose jobs of this user group", setOwnerGroup )
Script.registerSwitch( "S:", "status=", "choose jobs in this primary status", setStatus )
Script.registerSwitch( "e:", "site=", "choose jobs at this execution site", setSite )
Script.registerSwitch( "G:", "jobgroup=", "choose jobs from this job group", setJobGroup )
Script.registerSwitch( "D:", "date=", "Date in YYYY-MM-DD format, if not specified default is today", setDate )
Script.registerSwitch( "v", "verbose", "detailed information about jobs", setVerbose )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [options] JobID' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:     DIRAC job ID',] )
                        )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Core.Utilities.PrettyPrint import printTable
dirac = Dirac()
exitCode = 0

jobs = []
if len(args) > 0:
  jobs += args

if not jobs:
  result = dirac.selectJobs( status = status,
                             site = site,
                             owner = owner,
                             jobGroup = jobGroup,
                             date = date )
  
  if not result['OK']:
    print 'ERROR %s' % result['Message']
    DIRACexit( 2 )
  else:
    jobs = result['Value']
  
try:
  jobs = [ int( job ) for job in jobs ]
except Exception, x:
  print 'Expected integer for jobID'
  exitCode = 2
  DIRACexit( exitCode )

result = dirac.status( jobs )
if result['OK']:
  fields = ['JobID','Status','MinorStatus','Site']
  records = []
  for job in result['Value']:
    record = [str( job )]
    for key in fields[1:]:
      record.append( str( result['Value'][job][key] ) )
    records.append( record )
  print  
  printTable( fields, records )  
    
else:
  exitCode = 2
  print "ERROR: %s" % result['Message']

DIRACexit( exitCode )  