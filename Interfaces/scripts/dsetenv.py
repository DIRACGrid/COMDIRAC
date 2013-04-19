#!/usr/bin/env python

"""
register DCommands session environment variables
"""

import os

from COMDIRAC.Interfaces import critical

from COMDIRAC.Interfaces import DSession

if __name__ == "__main__":
  import sys

  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [[section.]option=value]...' % Script.scriptName,
                                       'Arguments:',
                                       '  section:     section (defaults to "session:environment")',
                                       '  option:      option name',
                                       '  value:       value to be set',] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )

  modified = False
  for arg in args:
    section = None
    option = None

    arg, value = arg.split( "=", 1 )
    if "." in arg:
      section, option = arg.split( ".", 1 )
    else:
      option = arg

    if section:
      session.set( section, option, value )
    else:
      session.setEnv( option, value )
    modified = True

  if modified:
    session.write( )
