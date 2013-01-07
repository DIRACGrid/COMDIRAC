#!/usr/bin/env python

"""
manage DCommands configuration file
"""

import os
import os.path
import stat

from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

import DIRAC
from DIRAC import S_OK, S_ERROR

def error( msg ):
  print msg

def critical( msg ):
  error( msg )
  DIRAC.exit( -1 )

class DConfig( object ):
  def __init__( self, configDir = os.path.expanduser( "~/.dirac" ),
                configFilename = "dcommands.conf" ):
    try:
      self.config = SafeConfigParser( allow_no_value = True )
    except TypeError:
      self.config = SafeConfigParser( )
    self.configDir = configDir
    self.configFilename = configFilename
    self.configPath = os.path.join( self.configDir, self.configFilename )
    self.bootstrapFile( )

  def bootstrapFile( self ):
    if not os.path.exists( self.configDir ):
      os.mkdir( self.configDir )
      os.chmod( self.configDir, stat.S_IRWXU )
    elif not os.path.isdir( self.configDir ):
      critical( "\"%s\" config dir is not a directory" % self.configDir )
    elif not os.stat( self.configDir ).st_mode != stat.S_IRWXU:
      critical( "\"%s\" config dir doesn't have correct permissions" % self.configDir )

    if os.path.isfile( self.configPath ):
      self.config.read( self.configPath )

  def write( self ):
    file = open( self.configPath, "w" )
    self.config.write( file )
    file.close( )

  def has( self, section, option ):
    return self.config.has_option( section, option )

  def get( self, section, option = None, defaultValue = None ):
    value = defaultValue
    try:
      if not option:
        return S_OK( self.config.items( section ) )
      value = self.config.get( section, option )
    except NoOptionError:
      if defaultValue == None:
        return S_ERROR( "Option \"%s\" missing in section \"%s\" from configuration \"%s\"" % ( option, section, self.configPath ) )
    except NoSectionError:
      if defaultValue == None:
         return S_ERROR( "Section missing \"%s\" from configuration \"%s\"" % ( section, self.configPath ) )
    return S_OK( value )

  def set( self, section, option = None, value = "" ):
    if section.lower( ) != "default" and not self.config.has_section( section ):
      self.config.add_section( section )
    if option:
      self.config.set( section, option, value )

  def remove( self, section, option = None ):
    if option:
      if not self.config.has_section( section ):
        return S_ERROR( "No such section \"%s\" in file \"%s\"" % ( section, self.configFilename) )
      self.config.remove_option( section, option )
    else:
      self.config.remove_setcion( self, section )

    return S_OK( )

  def hasProfile( self, profile ):
    return self.config.has_section( profile )

  def defaultProfile( self ):
    retVal = self.get( "global", "default_profile" )
    if not retVal[ "OK" ]: return None
    return retVal[ "Value" ]

  def sections( self ):
    return self.config.sections( )

  def items( self, section ):
    return self.config.items( section )

def createMinimalConfig( configDir = os.path.expanduser( "~/.dirac" ),
                         configFilename = "dcommands.conf" ):
  def existsOrCreate( section, option, value ):
    if dconfig.config.has_section( section ) and dconfig.config.has_option( section, option ):
      return False
    dconfig.set( section, option, value )
    return True

  dconfig = DConfig( configDir, configFilename )
  modified = False

  modified |= existsOrCreate( "global", "default_profile", "dirac_user" )
  modified |= existsOrCreate( "dirac_user", "group_name", "dirac_user" )
  modified |= existsOrCreate( "dirac_user", "home_dir", "/" )
#  modified |= existsOrCreate( "", "", "" )

  if modified: dconfig.write( )
