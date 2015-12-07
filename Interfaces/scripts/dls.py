#!/usr/bin/env python

"""
list FileCatalog file or directory
"""

import getopt

from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import createCatalog
from COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":
  import sys
  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.long = False
      self.replicas = False
      self.time = False
      self.reverse = False
      self.numericid = False
      self.size = False
      self.human = False

    def setLong( self, arg = None ):
      self.long = True

    def getLong( self ):
      return self.long

    def setReplicas( self, arg = None ):
      self.replicas = True

    def getReplicas( self ):
      return self.replicas

    def setTime( self, arg = None ):
      self.time = True

    def setReverse( self, arg = None ):
      self.reverse = True

    def setNumericID( self, arg = None ):
      self.numericid = True

    def setSize( self, arg = None ):
      self.size = True

    def setHuman( self, arg = None ):
      self.human = True

    def getTime( self ):
      return self.time

    def getReverse( self ):
      return self.reverse

    def getNumericID( self ):
      return self.numericid

    def getSize( self ):
      return self.size

    def getHuman( self ):
      return self.human

  params = Params( )

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] [path]' % Script.scriptName,
                                       'Arguments:',
                                       ' path:     file/directory path',
                                       '', 'Examples:',
                                       '  $ dls',
                                       '  $ dls ..',
                                       '  $ dls /',
                                       ] )
                          )
  Script.registerSwitch( "l", "long", "detailled listing", params.setLong )
  Script.registerSwitch( "L", "list-replicas", "detailled listing with replicas", params.setReplicas )
  Script.registerSwitch( "t", "time", "time based order", params.setTime )
  Script.registerSwitch( "r", "reverse", "reverse sort order", params.setReverse )
  Script.registerSwitch( "n", "numericid", "numeric UID and GID", params.setNumericID )
  Script.registerSwitch( "S", "size", "size based order", params.setSize )
  Script.registerSwitch( "H", "human-readable","size human readable", params.setHuman )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

  session = DSession( )

  Script.enableCS( )

  fccli = None

  if params.getReplicas( ):
    fccli = FileCatalogClientCLI( createCatalog( ) )
    params.setLong( None )
  else:
    fccli = FileCatalogClientCLI( createCatalog( ) )

  optstr = ""
  if params.long:       optstr += "l"
  if params.time:       optstr += "t"
  if params.repliacs:   optstr += "L"
  if params.reverse:    optstr += "r"
  if params.numericid:  optstr += "n"
  if params.size:       optstr += "S"
  if params.human:      optstr += "H"

  if optstr: optstr = "-" + optstr + " "
  # Need to check which was given the last 't' or 'S'
  # This would introduce some duplication of code :-(
  if params.long and params.time and params.size:
    short_opts = 'lLtrnSH'
    long_opts = ['long','timeorder','reverse','numericid','sizeorder','human-readable']
    try:
      optlist, arguments = getopt.getopt( sys.argv[1:],short_opts,long_opts )
      options = [ opt for (opt, arg) in optlist ]
      options = [ w.replace('--sizeorder','-S') for w in options ]
      options = [ w.replace('--timeorder','-t') for w in options ]
      options.reverse()
      # The last ['-S','-t'] provided is the one we use: reverse order
      # means that the last provided has the smallest index.
      # Indeed, setTime/setSize dont has impact: the important thing is
      # to add '-S'/'-t' at the end, then do_ls takes care of the rest.
      if options.index('-S') < options.index('-t'):
        params.setTime( False )
        optstr = optstr + '-S '
      else:
        params.setSize( False )
        optstr = optstr + '-t '

    except getopt.GetoptError, e:
      print str(e)
      print fccli.do_ls.__doc__
      exit(1)

  for p in pathFromArguments( session, args ):
    print "%s:" % p
    fccli.do_ls( optstr + p )

