#!/usr/bin/env python

"""
Change current DIRAC File Catalog working directory
"""

import os

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog

from DIRAC.Core.Base import Script

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [Path]' % Script.scriptName,
                                     'Arguments:',
                                     '  Path:     path to new working directory (defaults to home directory)',
                                     '', 'Examples:',
                                     '  $ dcd /dirac/user',
                                     '  $ dcd',
                                     ] )
                        )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

session = DSession( )

if len( args ) > 1:
  print "Error: too many arguments provided\n%s:" % Script.scriptName
  Script.showHelp( )
  DIRAC.exit( -1 )

if len( args ):
  arg = args[ 0 ]
  if not os.path.isabs( arg ):
    arg = os.path.normpath( os.path.join( session.getCwd( ), arg ))
else:
  arg = session.homeDir( )

Script.enableCS( )

catalog = DCatalog( )

if catalog.isDir( arg ):
  if( session.getCwd( ) != arg ):
    session.setCwd( arg )
    session.write( )
else:
  critical( "Error: \"%s\" not a valid directory" % arg )

