#!/usr/bin/env python

"""
Change current DIRAC File Catalog working directory
"""

import os

from DIRAC.Resources.Catalog.FileCatalogFactory import FileCatalogFactory


from DIRAC.COMDIRAC.Interfaces import critical
from DIRAC.COMDIRAC.Interfaces import DSession

def createCatalog( fctype = "FileCatalog" ):
  result = FileCatalogFactory( ).createCatalog( fctype )
  if not result[ 'OK' ]:
    print result[ 'Message' ]
    return None

  catalog = result[ 'Value' ]
  return catalog

class DCatalog( object ):
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
    arg = os.path.normpath( os.path.join( session.getCwd( ), arg ))

  return arg

def pathFromArguments( session, args ):
  ret = [ ]

  for arg in args:
    ret.append( pathFromArgument( session, arg ))

  return ret or [ session.getCwd( ) ]


