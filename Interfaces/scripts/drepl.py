#!/usr/bin/env python

"""
replicate file in the FileCatalog
"""

import os

import DIRAC

from DIRAC.COMDIRAC.Interfaces import critical
from DIRAC.COMDIRAC.Interfaces import DSession
from DIRAC.COMDIRAC.Interfaces import DCatalog
from DIRAC.COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.destinationSE = False
      self.sourceSE = False

    def setDestinationSE( self, arg ):
      self.destinationSE = arg
      return S_OK( )

    def getDestinationSE( self ):
      return self.destinationSE

    def setSourceSE( self, arg ):
      self.sourceSE = arg
      return S_OK( )

    def getSourceSE( self ):
      return self.sourceSE

  params = Params( )

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] lfn...' % Script.scriptName,
                                       'Arguments:',
                                       ' lfn:          file entry in the FileCatalog',] )
                          )
  Script.registerSwitch( "D:", "destination-se=", "Storage Element where to put replica (or a comma separated list)", params.setDestinationSE )
  Script.registerSwitch( "S:", "source-se=", "source Storage Element for replication", params.setSourceSE )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )
  catalog = DCatalog( )

  if len( args ) < 1:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  # default lfn: same file name as local_path
  lfns = pathFromArguments( session, args )

  # destination SE
  dsts = [ ]

  if params.destinationSE:
    dsts = params.destinationSE.split( "," )
  else:
    dsts = session.getReplicationSEs( )
    if not dsts:
      dsts = [ session.getEnv( "default_se", "DIRAC-USER" )[ "Value" ] ]

  srcopt = ""
  if params.sourceSE:
    srcopt = " " + params.sourceSE
  

  Script.enableCS( )

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI
  fccli = FileCatalogClientCLI( catalog.catalog )

  for lfn in lfns:
    for dst in dsts:
      #print "replicating", lfn, "to SE", dst
      fccli.do_replicate( lfn + " " + dst + srcopt )

