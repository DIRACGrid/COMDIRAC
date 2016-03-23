#! /usr/bin/env python

"""
remove DCommands session environment variables
"""

from COMDIRAC.Interfaces import critical

from COMDIRAC.Interfaces import DSession

if __name__ == "__main__":
  from COMDIRAC.Interfaces import ConfigCache
  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [[section.]option]...' % Script.scriptName,
                                       'Arguments:',
                                       '  section:     section (default: "session:environment")',
                                       '  option:      option name',] )
                          )

  configCache = ConfigCache()
  Script.parseCommandLine( ignoreErrors = True )
  configCache.cacheConfig()

  args = Script.getPositionalArgs()

  session = DSession( )

  modified = False
  for arg in args:
    section = None
    option = None

    if "." in arg:
      section, option = arg.split( "." )
    else:
      option = arg

    if section:
      session.remove( section, option )
    else:
      session.unsetEnv( option )

    modified = True

  if modified:
    session.write( )
