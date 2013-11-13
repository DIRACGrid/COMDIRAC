#!/usr/bin/env python

"""
Submit a job to the DIRAC Workload Management System
"""

from DIRAC.Core.Base import Script
from DIRAC import exit as DIRACexit

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [Job_jdl]' % Script.scriptName,
                                     'Arguments:',
                                     '  Job_jdl:     job JDL description',] )
                        )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

if len( args ) > 1:
  print "Error: too many arguments provided\n%s:" % Script.scriptName
  Script.showHelp( )
  DIRACexit( -1 )

from DIRAC.Interfaces.API.Dirac import Dirac
from types import StringTypes

dirac = Dirac()
exitCode = 0
errorList = []

for jdl in args:

  result = dirac.submit( jdl )
  if result['OK']:
    if type( result['Value'] ) in StringTypes:
      print result['Value']
    else:
      for jobID in result['Value']:  
        print jobID,
      print  
  else:
    errorList.append( ( jdl, result['Message'] ) )
    exitCode = 2

for error in errorList:
  print "ERROR %s: %s" % error

DIRACexit( exitCode )

