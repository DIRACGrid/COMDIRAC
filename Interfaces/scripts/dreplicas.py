#!/usr/bin/env python

"""
list replicas for files in the FileCatalog
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
                                       '  %s lfn...' % Script.scriptName,
                                       'Arguments:',
                                       '  lfn:     logical file name', ] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession()
  catalog = DCatalog()

  if len( args ) < 1:
    print "No argument provided\n%s:" % Script.scriptName
    Script.showHelp()
    DIRAC.exit( -1 )

  Script.enableCS()

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI
  fccli = FileCatalogClientCLI( catalog.catalog )

  for arg in args:
    # lfn
    lfn = pathFromArgument( session, args[ 0 ] )
    fccli.do_replicas( lfn )
