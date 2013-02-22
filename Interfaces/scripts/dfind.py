#!/usr/bin/env python

"""
find files in the FileCatalog
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
                                       '  %s [options] lfn metaspec...' % Script.scriptName,
                                       'Arguments:',
                                       ' lfn:         directory entry in the FileCatalog',
                                       ' metaspec:    metadata index specifcation (of the form: "meta=value" or "meta<value", "meta!=value", etc.)',
                                       '', 'Examples:',
                                       '  $ dfind . "some_integer_metadata>1"',
                                       ] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )
  catalog = DCatalog( )

  if len( args ) < 2:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  lfn = pathFromArgument( session, args[0] )

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI
  fccli = FileCatalogClientCLI( catalog.catalog )

  fccli.do_find( lfn + " " + " ".join( args[1:] ) )
