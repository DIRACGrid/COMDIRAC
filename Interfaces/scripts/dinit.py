#!/usr/bin/env python

"""
initialize DCommands session
"""

import os

import DIRAC
from DIRAC.COMDIRAC.Interfaces import DConfig, DSession, critical
from DIRAC.COMDIRAC.Interfaces.Utilities.DSession import sessionFromProxy
from DIRAC.Core.Base import Script

class Params:
  def __init__ ( self ):
    self.fromProxy = False
    self.destroy = False

  def setFromProxy( self, arg ):
    self.fromProxy = True

  def getFromProxy( self ):
    return self.fromProxy

  def setDestroy( self, arg ):
    self.destroy = True

  def getDestroy( self ):
    return self.destroy

params = Params( )

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [options] [profile_name]' % Script.scriptName,
                                     'Arguments:',
                                     ' profile_name:     existing profile section in DCommands config',] )
                        )
Script.registerSwitch( "p", "fromProxy", "build session from existing proxy", params.setFromProxy )
Script.registerSwitch( "D", "destroy", "destroy session information", params.setDestroy )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

retVal = Script.enableCS( )
if not retVal[ 'OK' ]:
  critical( retVal[ "Message" ] )

profile = None
if len( args ): profile = args[ 0 ]

if params.destroy:
  session = DSession( )
  os.unlink( session.configPath )
  DIRAC.exit( 0 )

session = None
if params.fromProxy:
  session = sessionFromProxy( )
else:
  session = DSession( profile )

if not session:
  print "Error: Session couldn't be initialized"
  DIRAC.exit( -1 )

session.write( )

session.checkProxyOrInit( )
retVal = session.proxyInfo( )
if not retVal[ "OK" ]:
  print retVal[ "Message" ]
  DIRAC.exit( -1 )

print retVal[ "Value" ]
