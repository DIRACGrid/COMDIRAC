#!/usr/bin/env python

"""
list FileCatalog file or directory
"""

import os

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import createCatalog
from COMDIRAC.Interfaces import pathFromArguments

if __name__ == "__main__":
  import sys
  from DIRAC.Core.Base import Script

  class Params:
    def __init__ ( self ):
      self.long = False
      self.replicas = False
      self.time = False

    def setLong( self, arg = None ):
      self.long = True

    def getLong( self ):
      return self.long

    def setReplicas( self, arg = None ):
      self.replicas = True

    def getReplicas( self ):
      return self.replicas

    def setTime( self, arg = None ):
      self.time = True

    def getTime( self ):
      return self.time

  params = Params( )

  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] [path]' % Script.scriptName,
                                       'Arguments:',
                                       ' path:     file/directory path',
                                       '', 'Examples:',
                                       '  $ dls',
                                       '  $ dls ..',
                                       '  $ dls /',
                                       ] )
                          )
  Script.registerSwitch( "l", "long", "detailled listing", params.setLong )
  Script.registerSwitch( "L", "list-replicas", "detailled listing with replicas", params.setReplicas )
  Script.registerSwitch( "t", "time", "time based order", params.setTime )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import DirectoryListing, FileCatalogClientCLI

  class ReplicaDirectoryListing( DirectoryListing ):
    def addFileWithReplicas( self,name,fileDict,numericid, replicas ):
      """ Pretty print of the file ls output with replica info
      """
      self.addFile( name, fileDict, numericid )
  
      self.entries[ -1 ] += tuple( replicas )
  
    def printListing( self,reverse,timeorder ):
      """
      """
      if timeorder:
        if reverse:
          self.entries.sort( key=lambda x: x[ 5 ] ) 
        else:  
          self.entries.sort( key=lambda x: x[ 5 ],reverse=True ) 
      else:  
        if reverse:
          self.entries.sort( key=lambda x: x[ 6 ],reverse=True ) 
        else:  
          self.entries.sort( key=lambda x: x[ 6 ] ) 
      
      # Determine the field widths
      wList = [ 0 for x in range( 7 ) ]
      for d in self.entries:
        for i in range( 7 ):
          if len( str( d[ i ] )) > wList[ i ]:
            wList[ i ] = len( str( d[ i ] ))
      
      for e in self.entries:
        print str( e[ 0 ] ),
        print str( e[ 1 ] ).rjust( wList[ 1 ] ),
        print str( e[ 2 ] ).ljust( wList[ 2 ] ),
        print str( e[ 3 ] ).ljust( wList[ 3 ] ),
        print str( e[ 4 ] ).rjust( wList[ 2 ] ),
        print str( e[ 5 ] ).rjust( wList[ 3 ] ),
        print str( e[ 6 ] )
  
        # print replicas if present
        if len( e ) > 7:
          for r in e[ 7: ]:
            print "  ", r
  
  class ReplicaFileCatalogClientCLI( FileCatalogClientCLI ):
    def getReplicas( self, path ):
      replicas = [ ]
      try:
        result = self.fc.getReplicas( path )    
        if result[ 'OK' ]:
          if result[ 'Value' ][ 'Successful' ]:
            for se,entry in result[ 'Value' ][ 'Successful' ][ path ].items( ):
              replicas.append( se.ljust( 15 ) + " " + entry )
          else:
            print "Replicas: ", result#[ 'Message' ]
      except Exception, x:
        replicas.append( "replicas failed:" + str( x ))
      return tuple( replicas )
  
    def do_ls( self, args ):
      """ Lists directory entries at <path> 
  
          usage: ls [ -ltrn ] <path>
      """

      argss = args.split( )
      # Get switches
      long = False
      reverse = False
      timeorder = False
      numericid = False
      path = self.cwd
      if len( argss ) > 0:
        if argss[ 0 ][ 0 ] == '-':
          if 'l' in argss[ 0 ]:
            long = True
          if 'r' in  argss[ 0 ]:
            reverse = True
          if 't' in argss[ 0 ]:
            timeorder = True
          if 'n' in argss[ 0 ]:
            numericid = True  
          del argss[ 0 ]  
            
        # Get path    
        if argss:        
          path = argss[ 0 ]       
          if path[ 0 ] != '/':
            path = self.cwd+'/'+path      
      path = path.replace( r'//','/' )
  
      # remove last character if it is "/"    
      if path[ -1 ] == '/' and path != '/':
        path = path[ :-1 ]

      # Check if the target path is a file
      result =  self.fc.isFile( path )          
      if not result[ 'OK' ]:
        print "Error: can not verify path"
        return
      elif path in result[ 'Value' ][ 'Successful' ] and result[ 'Value' ][ 'Successful' ][ path ]:
        result = self.fc.getFileMetadata( path )      
        dList = ReplicaDirectoryListing( )
        fileDict = result[ 'Value' ][ 'Successful' ][ path ]
  
        replicas = self.getReplicas( path )
  
        dList.addFileWithReplicas( os.path.basename( path ),fileDict,numericid, replicas )
        dList.printListing( reverse,timeorder )
        return         
      
      result = self.fc.isDirectory( path )
      if not result[ "OK" ]:
        print "Error: can not verify path"
        return
      elif path not in result[ 'Value' ][ 'Successful' ] or not result[ 'Value' ][ 'Successful' ][ path ]:
        print "Error: \"%s\" doesn't exist" % path
        return

      # Get directory contents now
      try:
        result =  self.fc.listDirectory( path,long )                     
        dList = ReplicaDirectoryListing( )
        if result[ 'OK' ]:
          if result[ 'Value' ][ 'Successful' ]:
            for entry in result[ 'Value' ][ 'Successful' ][ path ][ 'Files' ]:
              fname = entry.split( '/' )[ -1 ]
              # print entry, fname
              # fname = entry.replace( self.cwd,'' ).replace( '/','' )
              if long:
                fileDict = result[ 'Value' ][ 'Successful' ][ path ][ 'Files' ][ entry ][ 'MetaData' ]
                if fileDict:
                  replicas = self.getReplicas( os.path.join( path, fname ))
                  dList.addFileWithReplicas( fname,fileDict,numericid, replicas )
              else:  
                dList.addSimpleFile( fname )
            for entry in result[ 'Value' ][ 'Successful' ][ path ][ 'SubDirs' ]:
              dname = entry.split( '/' )[ -1 ]
              # print entry, dname
              # dname = entry.replace( self.cwd,'' ).replace( '/','' )  
              if long:
                dirDict = result[ 'Value' ][ 'Successful' ][ path ][ 'SubDirs' ][ entry ]
                if dirDict:
                  dList.addDirectory( dname,dirDict,numericid )
              else:    
                dList.addSimpleFile( dname )
            for entry in result[ 'Value' ][ 'Successful' ][ path ][ 'Links' ]:
              pass
                
            if long:
              dList.printListing( reverse,timeorder )      
            else:
              dList.printOrdered( )
        else:
          print "Error:",result[ 'Message' ]
      except Exception, x:
        print "Error:", str( x )

  session = DSession( )

  Script.enableCS( )

  fccli = None

  if params.getReplicas( ):
    fccli = ReplicaFileCatalogClientCLI( createCatalog( ) )
    params.setLong( None )
  else:
    fccli = FileCatalogClientCLI( createCatalog( ) )

  optstr = ""
  if params.long: optstr += "l"
  if params.time: optstr += "t"

  if optstr: optstr = "-" + optstr + " "

  for p in pathFromArguments( session, args ):
    print "%s:" % p
    fccli.do_ls( optstr + p )

