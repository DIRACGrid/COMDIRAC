#! /usr/bin/env python

"""
create a directory in the FileCatalog
"""

import os

import DIRAC
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Base import Script

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import createCatalog
from COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":

  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s Path...' % Script.scriptName,
                                       'Arguments:',
                                       '  Path:     path to new directory',
                                       '', 'Examples:',
                                       '  $ dmkdir ./some_lfn_dir',
                                       ] )
                          )

  configCache = ConfigCache()
  Script.parseCommandLine( ignoreErrors = True )
  configCache.cacheConfig()

  args = Script.getPositionalArgs()

  session = DSession( )

  if len( args ) < 1:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  catalog = createCatalog()

  result = catalog.createDirectory( pathFromArguments( session, args ) )
  if result["OK"]:
    if result["Value"]["Failed"]:
      for p in result["Value"]["Failed"]:
        print "ERROR - \"%s\": %s" % ( p, result["Value"]["Failed"][p] )
  else:
    print "ERROR: %s" % result["Message"]

