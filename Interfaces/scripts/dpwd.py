#! /usr/bin/env python

"""
print DCommands working directory
"""

if __name__ == "__main__":
  from DIRAC.Core.Base import Script
  from COMDIRAC.Interfaces import DSession
  from COMDIRAC.Interfaces import ConfigCache

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options]' % Script.scriptName,
                                       ] )
                          )

  configCache = ConfigCache()
  Script.parseCommandLine( ignoreErrors = True )
  configCache.cacheConfig()

  session = DSession()

  args = Script.getPositionalArgs()

  ret = session.getCwd( )

  print ret
