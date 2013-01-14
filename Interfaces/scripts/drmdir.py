#!/usr/bin/env python

"""
remove FileCatalog directories
"""

import os

import DIRAC

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import createCatalog
from COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [Path]...' % Script.scriptName,
                                       'Arguments:',
                                       '  Path:     directory path',] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )

  if len( args ) < 1:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  Script.enableCS( )

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI
  fccli = FileCatalogClientCLI( createCatalog( ) )

  for p in pathFromArguments( session, args ):
    fccli.do_rmdir( p )

