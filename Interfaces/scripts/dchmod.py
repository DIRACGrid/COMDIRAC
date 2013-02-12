#!/usr/bin/env python

"""
change file mode bits
"""

import os

import DIRAC

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArgument

from DIRAC.Core.Base import Script

class Params:
  def __init__ ( self ):
    self.recursive = False

  def setRecursive( self ):
    self.recursive = True

  def getRecursive( self ):
    return self.recursive

params = Params( )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [options] mode Path...' % Script.scriptName,
                                     'Arguments:',
                                     '  mode:     octal mode bits',
                                     '  Path:     path to file',
                                     '', 'Examples:',
                                     '  $ dchmod 755 ././some_lfn_file',
                                     '  $ dchmod -R 700 ./',
                                     ] )
                        )
Script.registerSwitch( "R", "recursive", "recursive", params.setRecursive )

Script.enableCS( )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

session = DSession( )
catalog = DCatalog( )

if len( args ) < 2:
  print "Error: not enough arguments provided\n%s:" % Script.scriptName
  Script.showHelp( )
  DIRAC.exit( -1 )

mode = args[ 0 ]

lfns = [ ]
for path in args[ 1: ]:
  lfns.append( pathFromArgument( session, path ))

optstr = ""
if params.recursive:
  optstr = "-R "

from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

fccli = FileCatalogClientCLI( catalog.catalog )

for lfn in lfns:
  fccli.do_chmod( optstr + mode + " " + lfn )
