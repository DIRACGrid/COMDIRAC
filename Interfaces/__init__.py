############################################################
# $HeadURL$
############################################################

"""
   COMDIRAC.Interfaces package
"""

__RCSID__ = "$Id$"

from Utilities.DConfig import DConfig, createMinimalConfig, guessProfilesFromCS, critical

from Utilities.DSession import DSession, getDNFromProxy

from Utilities.DCatalog import DCatalog, createCatalog, pathFromArgument, pathFromArguments

