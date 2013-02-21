#!/usr/bin/env python

"""
remove files from the FileCatalog (and all replicas from Storage Elements)
"""

import os

import DIRAC

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog

from COMDIRAC.Interfaces import pathFromArgument

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [lfn]...' % Script.scriptName,
                                       'Arguments:',
                                       '  lfn:     logical file name',
                                       '', 'Examples:',
                                       '  $ drm ./some_lfn_file',
                                       ] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )
  catalog = DCatalog( )

  if len( args ) < 1:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  lfns = [ ]
  for path in args:
    lfns.append( pathFromArgument( session, path ))

  from DIRAC.Interfaces.API.Dirac import Dirac
  dirac = Dirac( )

  exitCode = 0
  for lfn in lfns:
    result = dirac.removeFile( lfn, printOutput = False )
    if not result[ 'OK' ]:
      print 'ERROR %s: %s' % ( lfn, result[ 'Message' ] )
      exitCode = 2

  DIRAC.exit( exitCode )
