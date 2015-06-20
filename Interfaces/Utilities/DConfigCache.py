import os
import stat
import time
import cPickle

from DIRAC.Core.Base import Script
from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData

class ConfigCache:
  def __init__( self ):
    self.newConfig = True
    self.configCacheLifetime = 60.
    if "DCOMMANDS_PPID" in os.environ:
      self.pid = int( os.environ[ "DCOMMANDS_PPID" ] )
    else:
      self.pid = os.getppid()

    self.configCacheName = os.path.join( '/tmp', "DSession.configCache.%d.%d" % ( os.getuid(), self.pid ) )

    self.loadConfig()

  def loadConfig( self ):
    self.newConfig = True


    if os.path.isfile( self.configCacheName ):
      cacheStamp = os.stat( self.configCacheName ).st_mtime
      # print time.time() - cacheStamp, self.configCacheLifetime, time.time() - cacheStamp <= self.configCacheLifetime
      if time.time() - cacheStamp <= self.configCacheLifetime:
        gConfigurationData.remoteCFG = cPickle.load( open( self.configCacheName, "r" ) )
        Script.disableCS()
        self.newConfig = False

  def cacheConfig( self ):

    if self.newConfig:
      with open( self.configCacheName, "w" ) as f:
        os.chmod( self.configCacheName, stat.S_IRUSR | stat.S_IWUSR )
        cPickle.dump( gConfigurationData.remoteCFG, f )
