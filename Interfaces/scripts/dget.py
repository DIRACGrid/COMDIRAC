#! /usr/bin/env python

"""
download files from storage element
"""

import os

import DIRAC

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import error
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArgument

from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Base import Script

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s lfn... [local_dir]' % Script.scriptName,
                                     'Arguments:',
                                     ' lfn:          file to download',
                                     ' local_dir:   destination directory',
                                       '', 'Examples:',
                                       '  $ dget ./some_lfn_file /tmp',
                                       ] )
                        )

configCache = ConfigCache()
Script.parseCommandLine( ignoreErrors = True )
configCache.cacheConfig()

args = Script.getPositionalArgs()

session = DSession()
catalog = DCatalog()

from DIRAC.Interfaces.API.Dirac  import Dirac

dirac = Dirac()

if len( args ) < 1:
  error( "\nError: not enough arguments provided\n%s:" % Script.scriptName )
  Script.showHelp()
  DIRAC.exit( -1 )

# lfn
lfn = pathFromArgument( session, args[0] )

localDir = os.getcwd()
lfns = [( lfn, localDir )]

if len( args ) > 1:
  # localDir provided must be last argument
  localDir = args[-1]
  lfns = [( pathFromArgument( session, lfn ), localDir ) for lfn in args[:-1]]

  if not os.path.isdir( localDir ):
    critical( "Error: Destination local path must be a directory", -1 )

exitCode = 0
errmsgs = []

for lfn, localDir in lfns:
  ret = dirac.getFile( lfn, localDir )
  if not ret['OK']:
    exitCode = -2
    error( 'ERROR: %s' % ret['Message'] )

DIRAC.exit( exitCode )
