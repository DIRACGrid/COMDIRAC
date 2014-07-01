#!/usr/bin/env python

"""
put files in the FileCatalog (and Storage Element)

When destination SE is not specified, dput will use COMDIRAC configuration option "default_se".
"""

import os

import DIRAC
from DIRAC import S_OK, S_ERROR

from COMDIRAC.Interfaces import error
from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArgument

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.destinationSE = False

    def setDestinationSE( self, arg ):
      self.destinationSE = arg
      return S_OK()

    def getDestinationSE( self ):
      return self.destinationSE

  params = Params()

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] local_path[... lfn]' % Script.scriptName,
                                       'Arguments:',
                                       ' local_path:   local file',
                                       ' lfn:          file or directory entry in the file catalog',
                                       '', 'Examples:',
                                       '  $ dput some_local_file ./some_lfn_file',
                                       '  $ dput local_file1 local_file2 ./some_lfn_dir/',
                                       ] )
                          )
  Script.registerSwitch( "D:", "destination-se=", "Storage Element where to put replica", params.setDestinationSE )


  Script.parseCommandLine( ignoreErrors = False )
  args = Script.getPositionalArgs()

  session = DSession()
  catalog = DCatalog()

  from DIRAC.Interfaces.API.Dirac  import Dirac

  dirac = Dirac()

  if len( args ) < 1:
    error( "Error: No argument provided\n%s:" % Script.scriptName )
    Script.showHelp()
    DIRAC.exit( 0 )

  # local file
  local_path = args[ 0 ]

  # default lfn: same file name as local_path
  lfn = pathFromArgument( session, os.path.basename( local_path ) )

  pairs = [ ( local_path, lfn ) ]

  if len( args ) > 1:
    # lfn provided must be last argument
    lfn = pathFromArgument( session, args[ -1 ] )
    local_paths = args[ :-1 ]
    pairs = [ ]

    if catalog.isDir( lfn ):
      # we can accept one ore more local files
      for lp in local_paths:
        pairs.append( ( lp, os.path.join( lfn, os.path.basename( lp ) ) ) )
    else:
      if len( local_paths ) > 1:
        critical( "Error: Destination LFN must be a directory when registering multiple local files" )

      # lfn filename replace local filename
      pairs.append( ( local_path, lfn ) )

  # destination SE
  se = params.getDestinationSE()
  if not se:
    retVal = session.getEnv( "default_se", "DIRAC-USER" )
    if not retVal[ "OK" ]:
      error( retVal[ "Message" ] )
    se = retVal[ "Value" ]

  Script.enableCS()

  exitCode = 0

  for local_path, lfn in pairs:
    ret = dirac.addFile( lfn, local_path, se, printOutput = False )

  if not ret['OK']:
    exitCode = -2
    error( lfn + ': ' + ret['Message'] )

DIRAC.exit( exitCode )

