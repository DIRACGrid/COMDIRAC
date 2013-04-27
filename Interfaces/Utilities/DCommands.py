
import os
import os.path
import re
import uuid
import stat
import json
import random

from types import ListType, DictType
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

import DIRAC
from DIRAC  import S_OK, S_ERROR
import DIRAC.Core.Security.ProxyInfo as ProxyInfo
import DIRAC.FrameworkSystem.Client.ProxyGeneration as ProxyGeneration
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.Core.Security import Locations, VOMS
from DIRAC.Resources.Catalog.FileCatalogFactory import FileCatalogFactory

def error( msg ):
  print msg

def critical( msg ):
  error( msg )
  DIRAC.exit( -1 )

def _getProxyLocation():
  return Locations.getProxyLocation()

def _getProxyInfo( proxyPath = False ):
  if not proxyPath:
    proxyPath = _getProxyLocation()

  proxy_info = ProxyInfo.getProxyInfo( proxyPath, False )

  return proxy_info

def listFormatPretty( summaries, headers = None, sortKeys = None ):
  headerWidths = {}
  for i, c in enumerate( headers ):
    headerWidths[i] = len( c )

  for s in summaries:
    for i, v in enumerate( s ):
      l = len ( str( v ) )
      if l > headerWidths[i]:
        headerWidths[i] = l

  ret = ""
  for i, header in enumerate( headers ):
    ret += "{field:^{width}} ".format( field = header, width = headerWidths[i] )
  ret += "\n"
  for i, header in enumerate( headers ):
    ret += "{field} ".format( field = "-" * headerWidths[i] )
  ret += "\n"

  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    for i, header in enumerate( headers ):
      ret += "{field:^{width}} ".format( field = s[i], width = headerWidths[i] )
    ret += "\n"

  return ret

def listFormatCSV( summaries, headers = None, sortKeys = None ):
  ret = ""
  for header in headers:
    ret += header + ","
  ret += "\n"

  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    for i, header in enumerate( headers ):
      ret += str( s[i] ) + ","
    ret += "\n"
  return ret

def listFormatJSON( summaries, headers = None, sortKeys = None ):
  l = []
  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    d = {}
    for j, header in enumerate( headers ):
      d[header] = s[j]
    l.append( d )

  return json.dumps( l )

class ArrayFormatter:
  fmts = {"csv" : listFormatCSV, "pretty" : listFormatPretty, "json" : listFormatJSON}

  def __init__( self, outputFormat ):
    self.outputFormat = outputFormat

  def listFormat( self, list_, headers, sort = None ):
    if self.outputFormat not in self.fmts:
      return S_ERROR( "ArrayFormatter: Output format not supported: %s not in %s" %
                      ( self.outputFormat, self.fmts.keys() ) )

    if headers is None:
      if len( list_ ) == 0:
        return S_OK( "" )
      headers = range( list_ )

    sortKeys = None
    if sort is not None:
      sortKeys = []
      for i, s in enumerate( list_ ):
        sortKeys.append( ( s[sort], i ) )
      sortKeys.sort()

    return self.fmts[self.outputFormat]( list_, headers, sortKeys )

  def dictFormat( self, dict_, headers = None, sort = None ):
    if headers is None: headers = dict_.keys()
    list_ = []
    for v in dict_.values():
      row = []
      for h in headers:
        row.append( v[h] )
      list_.append( row )

    if sort is not None:
      sort = headers.index( sort )

    return self.listFormat( list_, headers, sort )

class DConfig( object ):
  def __init__( self, configDir = None, configFilename = "dcommands.conf" ):
    try:
      self.config = SafeConfigParser( allow_no_value = True )
    except TypeError:
      self.config = SafeConfigParser()

    if not configDir:
      var = "DCOMMANDS_CONFIG_DIR"
      if var in os.environ:
        configDir = os.environ[ var ]
      else:
        configDir = os.path.expanduser( "~/.dirac" )

    self.configDir = configDir
    self.configFilename = configFilename
    self.configPath = os.path.join( self.configDir, self.configFilename )
    self.bootstrapFile()

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
    file.close()

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
    if section.lower() != "default" and not self.config.has_section( section ):
      self.config.add_section( section )
    if option:
      self.config.set( section, option, value )

  def remove( self, section, option = None ):
    if option:
      if not self.config.has_section( section ):
        return S_ERROR( "No such section \"%s\" in file \"%s\"" % ( section, self.configFilename ) )
      self.config.remove_option( section, option )
    else:
      self.config.remove_setcion( self, section )

    return S_OK()

  def hasProfile( self, profile ):
    return self.config.has_section( profile )

  def defaultProfile( self ):
    retVal = self.get( "global", "default_profile" )
    if not retVal[ "OK" ]: return None
    return retVal[ "Value" ]

  def sections( self ):
    return self.config.sections()

  def items( self, section ):
    return self.config.items( section )

  def existsOrCreate( self, section, option, value ):
    if self.config.has_section( section ) and self.config.has_option( section, option ):
      return False
    self.set( section, option, value )
    return True

  def fillMinimal( self ):
    modified = False
    modified |= self.existsOrCreate( "global", "default_profile", "dirac_user" )
    modified |= self.existsOrCreate( "dirac_user", "group_name", "dirac_user" )
    modified |= self.existsOrCreate( "dirac_user", "home_dir", "/" )
    modified |= self.existsOrCreate( "dirac_user", "default_se", "DIRAC-USER" )

    return modified

def createMinimalConfig( configDir = os.path.expanduser( "~/.dirac" ),
                            configFilename = "dcommands.conf" ):

  dconfig = DConfig( configDir, configFilename )

  modified = dconfig.fillMinimal()

  if modified: dconfig.write()

def guessProfilesFromCS( DN ):
  cfg = DIRAC.gConfig

  # determine user name
  usersPath = "/Registry/Users"
  result = cfg.getSections( usersPath )
  if not result["OK"]: return result

  userName = None
  users = result["Value"]
  for u in users:
    result = cfg.getOption( "%s/%s/DN" % ( usersPath, u ) )
    if not result["OK"]:
      # silently skip misconfigured users
      continue
    if result["Value"] == DN:
      userName = u

  if not userName: return S_ERROR( "Could not find user with DN: %s" % DN )

  # build list of groups user belongs to
  groupsPath = "/Registry/Groups"
  result = cfg.getSections( groupsPath )
  if not result["OK"]: return result

  userGroups = []
  groups = result["Value"]
  for g in groups:
    result = cfg.getOption( "%s/%s/Users" % ( groupsPath, g ) )
    if not result["OK"]:
      # silently skip misconfigured groups
      continue

    users = map( lambda e: e.strip(), result["Value"].split( "," ) )
    if userName in users:
      userGroups.append( g )

  profiles = {}
  for g in userGroups:
    profiles[g] = {"group_name" : g}
  # guess a decent home directory

  for g in userGroups:
    profiles[g]["home_dir"] = "/"
    result = cfg.getOption( "%s/%s/VOMSVO" % ( groupsPath, g ) )
    if not result["OK"]:
      # silently skip misconfigured groups
      continue

    profiles[g]["home_dir"] = "/%s/user/%s/%s" % ( result["Value"], userName[0], userName )

  return S_OK( profiles )

class DSession( DConfig ):
  __ENV_SECTION = "session:environment"

  @classmethod
  def sessionFilePrefix( cls ):
    return "dsession.%x" % ( uuid.getnode(), )

  @classmethod
  def sessionFilename( cls, pid ):
    return cls.sessionFilePrefix() + ".%d" % ( pid, )

  def __init__( self, profileName = None, config = None, sessionDir = None, pid = None ):
    self.origin = config or DConfig()
    modified = self.origin.fillMinimal()
    if modified: self.origin.write()

    self.pid = pid
    if not self.pid:
      if "DCOMMANDS_PPID" in os.environ:
        self.pid = int( os.environ[ "DCOMMANDS_PPID" ] )
      else:
        self.pid = os.getppid()

    if not sessionDir:
      var = "DCOMMANDS_SESSION_DIR"
      if var in os.environ:
        sessionDir = os.environ[ var ]
      else:
        sessionDir = self.origin.configDir

    super( DSession, self ).__init__( sessionDir,
                                      self.sessionFilename( self.pid ) )

    self.__cleanSessionDirectory()

    oldProfileName = self.getEnv( "profile_name", "" )[ "Value" ]
    profileName = profileName or oldProfileName or self.origin.defaultProfile()
    self.profileName = profileName

    if not os.path.isfile( self.configPath ) or self.profileName != oldProfileName:
      self.__clearEnv()
      # set default common options from section [global]
      self.copyProfile( "global" )
      # overwrite with options from profile section
      self.copyProfile()
      # add profile name
      self.setEnv( "profile_name", self.profileName )
      # set working directory option
      self.setCwd( self.homeDir() )

  def __cleanSessionDirectory( self ):
    sessionPat = "^" + self.sessionFilePrefix() + "\.[0-9]+$"
    sessionRe = re.compile( sessionPat )
    for f in os.listdir( self.configDir ):
      if sessionRe.match( f ):
        if f != self.configFilename:
          os.unlink( os.path.join( self.configDir, f ) )

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

  def copyProfile( self, profileName = None ):
    for o, v in self.origin.items( profileName or self.profileName ):
      self.setEnv( o, v )

  def homeDir( self ):
    return self.getEnv( "home_dir", "/" )[ "Value" ]

  def getCwd( self ):
    return self.getEnv( "cwd", self.homeDir() )[ "Value" ]

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

  def getJDL( self ):
    return self.getEnv( "jdl", "" )["Value"]

  def proxyInfo( self, proxyPath = None ):
    return _getProxyInfo( proxyPath )

  def proxyIsValid( self, timeLeft = 60 ):
    proxy_path = _getProxyLocation()
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
    params = ProxyGeneration.CLIParams()
    retVal = self.getEnv( "group_name" )
    if not retVal[ "OK" ]:
      raise Exception( retVal[ "Message" ] )

    params.diracGroup = retVal[ "Value" ]

    result = ProxyGeneration.generateProxy( params )

    if not result[ "OK" ]:
      raise Exception( result[ "Message" ] )

    try:
      self.addVomsExt( result[ "Value" ] )
    except:
      # silently skip VOMS errors
      pass

  def addVomsExt( self, proxy ):
    retVal = self.getEnv( "group_name" )
    if not retVal[ "OK" ]:
      raise Exception( retVal[ "Message" ] )

    group = retVal[ "Value" ]
    vomsAttr = Registry.getVOMSAttributeForGroup( group )
    if not vomsAttr:
      raise Exception( "Requested adding a VOMS extension but no VOMS attribute defined for group %s" % group )

    result = VOMS.VOMS().setVOMSAttributes( proxy, attribute = vomsAttr, vo = Registry.getVOForGroup( group ) )
    if not result[ 'OK' ]:
      raise Exception( "Could not add VOMS extensions to the proxy\nFailed adding VOMS attribute: %s" % result[ 'Message' ] )

    chain = result[ 'Value' ]
    chain.dumpAllToFile( proxy )

  def checkProxyOrInit( self ):
    create = False
    try:
      create = not self.proxyIsValid()
    except:
      create = True

    if create:
      self.proxyInit()

  def getUserName( self ):
    proxyPath = _getProxyLocation()
    if not proxyPath:
      return S_ERROR( "no proxy location" )
    retVal = self.proxyInfo()
    if not retVal["OK"]: return retVal

    return S_OK( retVal["Value"]["username"] )

def guessConfigFromCS( config, section, userName, groupName ):
  '''
  try to guess best DCommands default values from Configuration Server
  '''
  # write group name
  config.set( section, "group_name", groupName )

  # guess FileCatalog home directory
  vo = gConfig.getValue( "/Registry/Groups/%s/VO" % groupName )
  firstLetter = userName[0]
  homeDir = "/%s/user/%s/%s" % ( vo, firstLetter, userName )

  config.set( section, "home_dir", homeDir )

  # try to guess default SE DIRAC name
  voDefaultSEName = "VO_%s_DEFAULT_SE" % vo.upper()
  voDefaultSEName = voDefaultSEName.replace( ".", "_" )
  voDefaultSEName = voDefaultSEName.replace( "-", "_" )
  try:
    voDefaultSEHost = os.environ[ voDefaultSEName ]
  except KeyError:
    voDefaultSEHost = None
  if voDefaultSEHost:
    retVal = gConfig.getSections( "/Resources/StorageElements" )
    if retVal[ "OK" ]:
      defaultSESite = None
      for seSite in retVal[ "Value" ]:
        # look for a SE with same host name
        host = gConfig.getValue( "/Resources/StorageElements/%s/AccessProtocol.1/Host" % seSite )
        if host and host == voDefaultSEHost:
          # check if SE has rw access
          retVal = gConfig.getOptionsDict( "/Resources/StorageElements/%s" %
                                          seSite )
          if retVal[ "OK" ]:
            od = retVal[ "Value" ]
            r = "ReadAccess"
            w = "WriteAccess"
            active = "Active"
            ok = r in od and od[ w ] == active
            ok &= w in od and od[ w ] == active

            if ok:
              defaultSESite = seSite
          # don't check other SE sites
          break

      if defaultSESite:
        #write to config
        config.set( section, "default_se", defaultSESite )

def sessionFromProxy( config = DConfig(), sessionDir = None ):
  proxyPath = _getProxyLocation()
  if not proxyPath:
    print "No proxy found"
    return None

  retVal = _getProxyInfo( proxyPath )
  if not retVal[ "OK" ]:
    raise Exception( retVal[ "Message" ] )

  pi = retVal[ "Value" ]
  try:
    groupName = pi[ "group" ]
  except KeyError:
    groupName = None

  sections = config.sections()
  match = None

  for s in sections:
    if config.has( s, "group_name" ) and config.get( s, "group_name" )[ "Value" ] == groupName:
      match = s
      break

  if not match:
    if not groupName:
      raise Exception( "cannot guess profile defaults without a DIRAC group in Proxy" )

    match = "__guessed_profile__"
    userName = pi["username"]
    guessConfigFromCS( config, match, userName, groupName )

  session = DSession( match, config, sessionDir = sessionDir )

  # force copy of config profile options to environment
  session.copyProfile()

  return session

def getDNFromProxy():
  proxyPath = _getProxyLocation()
  if not proxyPath:
    print "No proxy found"
    return None

  retVal = _getProxyInfo( proxyPath )
  if not retVal[ "OK" ]:
    return retVal

  pi = retVal[ "Value" ]

  return S_OK( pi["identity"] )

def createCatalog( fctype = "FileCatalog" ):
  result = FileCatalogFactory().createCatalog( fctype )
  if not result[ 'OK' ]:
    print result[ 'Message' ]
    return None

  catalog = result[ 'Value' ]
  return catalog

class DCatalog( object ):
  """
  DIRAC File Catalog helper
  """
  def __init__( self, fctype = "FileCatalog" ):
    self.catalog = createCatalog( fctype )

  def isDir( self, path ):
    result = self.catalog.isDirectory( path )
    if result[ 'OK' ]:
      if result[ 'Value' ][ 'Successful' ]:
        if result[ 'Value' ][ 'Successful' ][ path ]:
          return True
    return False

  def isFile( self, path ):
    result = self.catalog.isFile( path )
    if result[ 'OK' ] and path in result[ 'Value' ][ 'Successful' ] and result[ 'Value' ][ 'Successful' ][ path ]:
      return True
    return False

  def getMeta( self, path ):
    if self.isDir( path ):
      return self.catalog.getDirectoryMetadata( path )
    return self.catalog.getFileUserMetadata( path )

def pathFromArgument( session, arg ):
  if not os.path.isabs( arg ):
    arg = os.path.normpath( os.path.join( session.getCwd(), arg ) )

  return arg

def pathFromArguments( session, args ):
  ret = [ ]

  for arg in args:
    ret.append( pathFromArgument( session, arg ) )

  return ret or [ session.getCwd() ]


