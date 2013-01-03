#!/usr/bin/env python

"""
manage DCommands session
"""

import os
import uuid

from DIRAC.COMDIRAC.Interfaces import DConfig

import DIRAC
from DIRAC import S_OK, S_ERROR
import DIRAC.Core.Security.ProxyInfo as ProxyInfo
import DIRAC.FrameworkSystem.Client.ProxyGeneration as ProxyGeneration
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.Core.Security import Locations, VOMS

import random

def _getProxyLocation( ):
  return Locations.getProxyLocation( )

def _getProxyInfo( proxyPath = False ):
  if not proxyPath:
    proxyPath = _getProxyLocation( )

  proxy_info = ProxyInfo.getProxyInfo( proxyPath, False )

  return proxy_info

class DSession( DConfig ):
  __ENV_SECTION = "session:environment"

  @classmethod
  def sessionFilename( cls, pid ):
    return "dsession.%x.%d" % (uuid.getnode( ), pid)

  def __init__( self, profileName = None, config = None, pid = None ):
    self.origin = config or DConfig( )
    self.pid = pid
    if not self.pid:
      if "DCOMMANDS_PPID" in os.environ:
        self.pid = int( os.environ[ "DCOMMANDS_PPID" ] )
      else:
        self = os.getppid( )

    super( DSession, self ).__init__( self.origin.configDir, self.sessionFilename( self.pid ) )

    old_profile_name = self.getEnv( "profile_name", "" )[ "Value" ]
    profileName = profileName or old_profile_name or  self.origin.defaultProfile( )
    self.profileName = profileName

    if not os.path.isfile( self.configPath ) or self.profileName != old_profile_name:
      self.__clearEnv( )
      self.copyProfile( )
      self.setEnv( "profile_name", self.profileName )
      self.setCwd( self.homeDir( ) )

  def getEnv( self, option, defaultValue = None ):
    return  self.get( DSession.__ENV_SECTION, option, defaultValue )

  def listEnv( self ):
    return self.get( DSession.__ENV_SECTION )

  def setEnv( self, option, value ):
    self.set( DSession.__ENV_SECTION, option, value )

  def unsetEnv( self, option ):
    return self.remove( DSession.__ENV_SECTION, option )

  def __clearEnv( self ):
    self.config.remove_section( DSession.__ENV_SECTION )

  def copyProfile( self ):
    for o, v in self.origin.items( self.profileName ):
      self.setEnv( o, v )

  def homeDir( self ):
    return self.getEnv( "home_dir", "/" )[ "Value" ]

  def getCwd( self ):
    return self.getEnv( "cwd", self.homeDir( ) )[ "Value" ]

  def setCwd( self, value ):
    self.setEnv( "cwd", value )

  def getReplicationSEs( self ):
    replication_scheme = self.getEnv( "replication_scheme", "all( )" )[ "Value" ]
    replication_ses = self.getEnv( "replication_ses", "" )[ "Value" ]

    if not replication_ses:
      return [ ]

    replication_ses = replication_ses.split( "," )

    def randomSEs( num ):
      random.shuffle( replication_ses )
      return replication_ses[ 0:num ]

    schemes = {
      "all": lambda : replication_ses,
      "first" : lambda num: replication_ses[ 0:num ],
      "random" : randomSEs,
      }

    return eval( replication_scheme, schemes )

  def proxyInfo( self, proxyPath = None ):
    return _getProxyInfo( proxyPath )

  def proxyIsValid( self, timeLeft = 60 ):
    proxy_path = _getProxyLocation( )
    if not proxy_path: return False

    retVal = self.proxyInfo( proxy_path )
    if not retVal[ "OK" ]:
      return False

    pi = retVal[ "Value" ]

    timeLeft = max( timeLeft, 0 )

    retVal = self.getEnv( "group_name" )
    if not retVal[ "OK" ]:
      return False
    group_name = retVal[ "Value" ]

    return ( pi[ "secondsLeft" ] > timeLeft and pi[ "validGroup" ] and
             pi[ "group" ] == group_name )

  def proxyInit( self ):
    params = ProxyGeneration.CLIParams( )
    retVal = self.getEnv( "group_name" )
    if not retVal[ "OK" ]:
      raise Exception( result[ "Message" ] )

    params.diracGroup = retVal[ "Value" ]

    result = ProxyGeneration.generateProxy( params )

    if not result[ "OK" ]:
      raise Exception( result[ "Message" ] )

    self.addVomsExt( result[ "Value" ] )

  def addVomsExt( self, proxy ):
    retVal = self.getEnv( "group_name" )
    if not retVal[ "OK" ]:
      raise Exception( result[ "Message" ] )

    group = retVal[ "Value" ]
    vomsAttr = Registry.getVOMSAttributeForGroup( group )
    if not vomsAttr:
      raise Exception( "Requested adding a VOMS extension but no VOMS attribute defined for group %s" % group )

    result = VOMS.VOMS( ).setVOMSAttributes( proxy, attribute = vomsAttr, vo = Registry.getVOForGroup( group ))
    if not result[ 'OK' ]:
      raise Exception( "Could not add VOMS extensions to the proxy\nFailed adding VOMS attribute: %s" % result[ 'Message' ] )

    chain = result[ 'Value' ]
    chain.dumpAllToFile( proxy )

  def checkProxyOrInit( self ):
    create = False
    try:
      create = not self.proxyIsValid( )
    except:
      create = True

    if create:
      self.proxyInit( )

def sessionFromProxy( config = DConfig( ) ):
  proxy_path = _getProxyLocation( )
  if not proxy_path:
    print "No proxy found"
    return None

  retVal = _getProxyInfo( proxy_path )
  if not retVal[ "OK" ]:
    raise Exception( retVal[ "Message" ] )

  pi = retVal[ "Value" ]
  try:
    group_name = pi[ "group" ]
  except KeyError:
    group_name = None

  sections = config.sections( )
  match = None

  for s in sections:
    if config.has( s, "group_name" ) and config.get( s, "group_name" )[ "Value" ] == group_name:
      match = s
      break

  if not match:
    raise KeyError( "Profile with group name \"%s\" not found in configuration." % group_name )

  return DSession( match, config )

