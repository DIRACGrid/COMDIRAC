#!/usr/bin/env python

"""
manipulate meteadata in the FileCatalog
"""

import os

import DIRAC
from DIRAC import S_OK, S_ERROR

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArgument

class DMetaCommand( object ):
  def run( self, lfn, metas ):
    raise NotImplementedError

class DMetaAdd( DMetaCommand ):
  def __init__( self, fcClient ):
    self.fcClient = fcClient

  def run( self, lfn, metas ):
    metadict = {}
    for meta in metas:
      name, value = meta.split( "=" )
      metadict[name] = value
    result = self.fcClient.fc.setMetadata( lfn, metadict )
    if not result[ "OK" ]:
      print "Error:", result

class DMetaRm( DMetaCommand ):
  def __init__( self, fcClient ):
    self.fcClient = fcClient

  def run( self, lfn, metas ):
    for meta in metas:
      self.fcClient.do_meta( "remove %s %s" % ( lfn, meta ))

class DMetaList( DMetaCommand ):
  def __init__( self, catalog ):
    self.catalog = catalog

  def run( self, lfn, metas ):
    retVal = self.catalog.getMeta( lfn )

    if not retVal[ "OK" ]:
      print "Error:", retVal[ "Message" ]
      DIRAC.exit( -1 )
    metadict = retVal[ "Value" ]

    if not metas:
      for k, v in metadict.items( ):
        print k+"="+str( v )
    else:
      for meta in metas:
        if meta in metadict.keys( ):
          print meta+"="+metadict[ meta ]

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.index = False
      self.listIndex = False

    def setIndex( self, arg ):
      print "index", arg
      self.index = arg
      return S_OK( )

    def getIndex( self ):
      return self.index

    def setListIndex( self, arg ):
      self.listIndex = True

    def getListIndex( self ):
      return self.listIndex


  params = Params( )

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s -I' % Script.scriptName,
                                       ' - list metadata indices',
                                       '++ OR ++',
                                       '  %s -i r meta...' % Script.scriptName,
                                       ' - delete metadata index',
                                       'Arguments:',
                                       ' meta:     metadata index to be deleted',
                                       '++ OR ++',
                                       '  %s -i f|d meta=(int|float|string|date)' % Script.scriptName,
                                       ' - add metadata index for files or directories',
                                       'Arguments:',
                                       ' meta=type:     metadata index to be added',
                                       '++ OR ++',
                                       '  %s add|rm|ls lfn meta[=value]...' % Script.scriptName,
                                       ' - manipulate metadata for lfn',
                                       'Arguments:',
                                       ' lfn:           path',
                                       ' meta:          metadata (with value for add)',] )
                          )
  Script.registerSwitch( "i:", "index=", "set or remove metadata indices", params.setIndex )
  Script.registerSwitch( "I", "list-index", "list defined metadata indices", params.setListIndex )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )
  catalog = DCatalog( )

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

  fccli = FileCatalogClientCLI( catalog.catalog )

  if params.getIndex( ):
    if params.getIndex( ) == "r":
      for meta in args:
        cmdline = "index -r %s" % meta
        #print cmdline
        fccli.do_meta( cmdline )
    else:
      for arg in args:
        meta, type = arg.split( "=" )
        cmdline = "index -%s %s %s" % ( params.getIndex( ), meta, type )
        #print cmdline
        fccli.do_meta( cmdline )
    DIRAC.exit( 0 )

  if params.getListIndex( ):
    fccli.do_meta( "show" )
    DIRAC.exit( 0 )

  meta_commands = {
    "add" : DMetaAdd( fccli ),
    "rm" : DMetaRm( fccli ),
    "ls" : DMetaList( catalog )
    }

  if len( args ) < 2:
    print "Error: Not enough arguments provided\n%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )

  command = args[ 0 ]

  if command not in meta_commands.keys( ):
    print "Error: Unknown dmeta command \"%s\"" % command
    print "%s:" % Script.scriptName
    Script.showHelp( )
    DIRAC.exit( -1 )


  command = meta_commands[ command ]

  lfn = pathFromArgument( session, args[ 1 ] )

  metas = args[ 2: ]

  command.run( lfn, metas )
