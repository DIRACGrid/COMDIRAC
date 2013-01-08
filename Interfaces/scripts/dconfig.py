#!/usr/bin/env python

"""
configure DCommands
"""

import sys

from DIRAC.Core.Base import Script

from DIRAC.COMDIRAC.Interfaces import DConfig, createMinimalConfig, critical

class Params:
  def __init__ ( self ):
    self.minimal = False

  def setMinimal( self, arg ):
    self.minimal = True

  def getMinimal( self ):
    return self.minimal

params = Params( )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [options] [section[.option[=value]]]...' % Script.scriptName,
                                     'Arguments:',
                                     ' section:     display all options in section',
                                     '++ OR ++',
                                     ' section.option:     display option',
                                     '++ OR ++',
                                     ' section.option=value:     set option value',] )
                        )
Script.registerSwitch( "m", "minimal", "verify and fill minimal configuration", params.setMinimal )

Script.enableCS( )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

if params.minimal:
  createMinimalConfig( )

dconfig = DConfig( )

modified = False

for arg in args:
  value = None
  section = None
  option = None
  if "=" in arg:
    arg, value = arg.split( "=" )
  if "." in arg:
    section, option = arg.split( "." )
  else:
    section = arg

  if value != None:
    dconfig.set( section, option, value )
    modified = True
  else:
    retVal = dconfig.get( section, option )
    if not retVal[ "OK" ]: critical( retVal[ "Message" ] )
    ret = retVal[ "Value" ]
    if type( ret ) == type( [ ] ):
      print "[%s]" % section
      for o, v in ret:
        print o, "=", v
    else:
      print option, "=", ret

if modified:
  dconfig.write( )
