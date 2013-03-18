#!/usr/bin/env python

"""
replicate file in the FileCatalog

Can work in two modes.

In the first mode, yuser provides the destination SE with option "-D".
In the second mode, when no destination is given, drepl will look for COMDIRAC configuration options "replication_scheme" and "replication_ses".
If found, those variables will define a list of SEs where to put replicas.
If not found drepl will fallback to configuration option "default_se".

Supported schemes for automated replication (in option "replication_scheme") are:
* all() - replicate file to all SEs listed in option "replication_ses"
* first(N) - replicate file to N first SEs listed in option "replication_ses"
* random(N) - replicatefile to N randomly chosen SEs from the list in option "replication_ses"

"""

import os

import DIRAC
from DIRAC import S_OK, S_ERROR

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.destinationSE = False
      self.sourceSE = False

    def setDestinationSE( self, arg ):
      self.destinationSE = arg
      return S_OK()

    def getDestinationSE( self ):
      return self.destinationSE

    def setSourceSE( self, arg ):
      self.sourceSE = arg
      return S_OK()

    def getSourceSE( self ):
      return self.sourceSE

  params = Params()

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] lfn...' % Script.scriptName,
                                       'Arguments:',
                                       ' lfn:          file entry in the FileCatalog',
                                       '', 'Examples',
                                      '  $ drepl ./some_lfn_file',
                                      '  $ drepl -D SOME-DESTINATION-SE-disk ./some_lfn_file',
                                       ] )
                          )
  Script.registerSwitch( "D:", "destination-se=", "Storage Element where to put replica (or a comma separated list)", params.setDestinationSE )
  Script.registerSwitch( "S:", "source-se=", "source Storage Element for replication", params.setSourceSE )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession()
  catalog = DCatalog()

  if len( args ) < 1:
    print "Error: No argument provided\n%s:" % Script.scriptName
    Script.showHelp()
    DIRAC.exit( -1 )

  # default lfn: same file name as local_path
  lfns = pathFromArguments( session, args )

  # destination SE
  dsts = [ ]

  if params.destinationSE:
    dsts = params.destinationSE.split( "," )
  else:
    dsts = session.getReplicationSEs()
    if not dsts:
      dsts = [ session.getEnv( "default_se", "DIRAC-USER" )[ "Value" ] ]

  srcopt = ""
  if params.sourceSE:
    srcopt = " " + params.sourceSE


  Script.enableCS()

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI
  fccli = FileCatalogClientCLI( catalog.catalog )

  for lfn in lfns:
    for dst in dsts:
      # print "replicating", lfn, "to SE", dst
      fccli.do_replicate( lfn + " " + dst + srcopt )

