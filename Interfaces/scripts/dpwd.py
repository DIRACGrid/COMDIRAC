#!/usr/bin/env python

"""
print DCommands working directory
"""

import os

from DIRAC.COMDIRAC.Interfaces import critical

from DIRAC.COMDIRAC.Interfaces import DSession

if __name__ == "__main__":
  import sys
  from DIRAC.Core.Base import Script

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options]' % Script.scriptName,] )
                          )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  session = DSession( )

  ret = session.getCwd( )

  print ret
