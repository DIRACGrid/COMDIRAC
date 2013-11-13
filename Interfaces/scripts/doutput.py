#!/usr/bin/env python

"""
Get output sandbox and/or data of executed jobs
"""

from DIRAC.Core.Base import Script
from DIRAC import exit as DIRACexit
from DIRAC import S_OK

outputDir = None
def setOutputDir( option ):
  global outputDir
  outputDir = option
  return S_OK()

jobFile = None
def setJobFile( option ):
  global jobFile
  jobFile = option
  return S_OK()

jobGroup = None
def setJobGroup( option ):
  global jobGroup
  jobGroup = option
  return S_OK()

getData = False
getSB = True
def setGetData( option ):
  global getData, getSB
  getData = True
  getSB = False
  return S_OK()

def setGetSB( option ):
  global getSB
  getSB = True
  return S_OK()

noJobDir = False
def setNoJobDir( option ):
  global noJobDir
  noJobDir = True
  return S_OK()

Script.registerSwitch( "D:", "dir=", "Store the output in this directory", setOutputDir )
Script.registerSwitch( "f:", "job-file=", "Get output for jobs with IDs from the file", setJobFile )
Script.registerSwitch( "g:", "job-group=", "Get output for jobs in the given group", setJobGroup )
Script.registerSwitch( "t", "output-data", "Get output data for jobs", setGetData )
Script.registerSwitch( "S", "sandbox", "Get output sandbox for jobs", setGetSB )
Script.registerSwitch( "n", "no-job-directory", "Do not create per job output directory", setNoJobDir )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [options] JobID' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:     DIRAC job ID',] )
                        )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

import os, shutil
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.Core.Utilities.Time import toString, date, day

dirac = Dirac()
exitCode = 0
errorList = []

jobs = []
if len(args) > 0:
  jobs += args

if jobGroup:
  jobDate = toString( date() - 30*day )
    
  # Choose jobs in final state, no more than 30 days old
  result = dirac.selectJobs( jobGroup=jobGroup, date=jobDate, status='Done' )
  if not result['OK']:
    if not "No jobs selected" in result['Message']:
      print "Error:", result['Message']
      DIRACexit( -1 )
  else:    
    jobs += result['Value']      
  result = dirac.selectJobs( jobGroup=jobGroup, date=jobDate, status='Failed' )
  if not result['OK']:
    if not "No jobs selected" in result['Message']:
      print "Error:", result['Message']
      DIRACexit( -1 )
  else:
    jobs += result['Value']     
    
if jobFile:
  if os.path.exists( jobFile ):
    jFile = open( jobFile )
    jobs += jFile.read().split()
    jFile.close()     
    
if jobGroup:
  if outputDir:
    outputDir = os.path.join( outputDir, jobGroup )
  else:
    outputDir = jobGroup  

if outputDir: 
  if not os.path.exists(outputDir):
    os.makedirs( outputDir)
else:
  outputDir = os.getcwd()    
  
print "Output directory is", outputDir  
  
jobs = [ str(job) for job in jobs ]
doneJobs = os.listdir( outputDir )
todoJobs = [ job for job in jobs if not job in doneJobs ]
  
for job in todoJobs:

  if getSB:
    result = dirac.getOutputSandbox( job, outputDir = outputDir, noJobDir = noJobDir )
    
    jobDir = str(job)
    if outputDir:
      jobDir = os.path.join( outputDir, job )
    if result['OK']:
      if os.path.exists( jobDir ):
        print 'Job output sandbox retrieved in %s/' % ( jobDir )
    else:
      if os.path.exists( '%s' % jobDir ):
        shutil.rmtree( jobDir )
      errorList.append( ( job, result['Message'] ) )
      exitCode = 2
      
  if getData:
    if not noJobDir:
      outputDir = "%s/%s" % ( outputDir, str( job ) )
    
    if not os.path.exists( outputDir ):
      os.makedirs( outputDir )
      
    result = dirac.getJobOutputData( job, destinationDir = outputDir )
    if result['OK']:
      print 'Job %s output data retrieved' % ( job )
    else:
      errorList.append( ( job, result['Message'] ) )
      exitCode = 2    

for error in errorList:
  print "ERROR %s: %s" % error

DIRACexit( exitCode )      