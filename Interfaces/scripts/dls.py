#!/usr/bin/env python

"""
list FileCatalog file or directory
"""

import os
import getopt

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
      self.reverse = False
      self.numericid = False
      self.size = False
      self.human = False

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

    def setReverse( self, arg = None ):
      self.reverse = True

    def setNumericID( self, arg = None ):
      self.numericid = True

    def setSize( self, arg = None ):
      self.size = True

    def setHuman( self, arg = None ):
      self.human = True

    def getTime( self ):
      return self.time

    def getReverse( self ):
      return self.reverse

    def getNumericID( self ):
      return self.numericid

    def getSize( self ):
      return self.size

    def getHuman( self ):
      return self.human

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
  Script.registerSwitch( "r", "reverse", "reverse sort order", params.setReverse )
  Script.registerSwitch( "n", "numericid", "numeric UID and GID", params.setNumericID )
  Script.registerSwitch( "S", "size", "size based order", params.setSize )
  Script.registerSwitch( "H", "human-readable","size human readable", params.setHuman )

  Script.parseCommandLine( ignoreErrors = True )
  args = Script.getPositionalArgs()

  from DIRAC.DataManagementSystem.Client.DirectoryListing import DirectoryListing
  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

  class ReplicaDirectoryListing( DirectoryListing ):
    def addFileWithReplicas( self,name,fileDict,numericid, replicas ):
      """ Pretty print of the file ls output with replica info
      """
      self.addFile( name, fileDict, replicas, numericid )
  
      self.entries[ -1 ] += tuple( replicas )
  
    def human_readable_size(self,num,suffix='B'):
      """ Translate file size in bytes to human readable

          Powers of 2 are used (1Mi = 2^20 = 1048576 bytes).
      """
      num = int(num)
      for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
          return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
      return "%.1f%s%s" % (num, 'Yi', suffix)

    def printListing( self,reverse,timeorder,sizeorder,humanread):
      """
      """
      if timeorder:
        if reverse:
          self.entries.sort( key=lambda x: x[ 5 ] ) 
        else:  
          self.entries.sort( key=lambda x: x[ 5 ],reverse=True ) 
      elif sizeorder:  
        if reverse:
          self.entries.sort(key=lambda x: x[4])
        else:  
          self.entries.sort(key=lambda x: x[4],reverse=True)
      else:  
        if reverse:
          self.entries.sort( key=lambda x: x[ 6 ],reverse=True ) 
        else:  
          self.entries.sort( key=lambda x: x[ 6 ] ) 
      
      # Determine the field widths
      wList = [0] * 7
      for d in self.entries:
        for i in range( 7 ):
          if humanread and i == 4:
            humanread_len = len( str( self.human_readable_size( d[ 4 ] )) )
            if humanread_len > wList[ 4 ]:
              wList[ 4 ] = humanread_len
          else:
            if len( str( d[ i ] )) > wList[ i ]:
              wList[ i ] = len( str( d[ i ] ))
      
      for e in self.entries:
        size = e[ 4 ]
        if humanread:
          size = self.human_readable_size(e[ 4 ])

        print str( e[ 0 ] ),
        print str( e[ 1 ] ).rjust( wList[ 1 ] ),
        print str( e[ 2 ] ).ljust( wList[ 2 ] ),
        print str( e[ 3 ] ).ljust( wList[ 3 ] ),
        print str(  size  ).rjust( wList[ 4 ] ),
        print str( e[ 5 ] ).rjust( wList[ 5 ] ),
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

          usage: ls [-ltrnSH] <path>

       -l  --long                : Long listing.
       -t  --timeorder           : List ordering by time.
       -r  --reverse             : Reverse list order.
       -n  --numericid           : List with numeric value of UID and GID.
       -S  --sizeorder           : List ordering by file size.
       -H  --human-readable      : Print sizes in human readable format (e.g., 1Ki, 20Mi);
                                   powers of 2 are used (1Mi = 2^20 B).
      """

      argss = args.split( )
      # Get switches
      long = False
      reverse = False
      timeorder = False
      numericid = False
      sizeorder = False
      humanread = False
      short_opts = 'ltrnSH'
      long_opts = ['long','timeorder','reverse','numericid','sizeorder','human-readable']
      path = self.cwd
      if len(argss) > 0:
        try:
          optlist, arguments = getopt.getopt(argss,short_opts,long_opts)
        except getopt.GetoptError, e:
          print str(e)
          print self.do_ls.__doc__
          return
        # Duplicated options are allowed: later options have precedence, e.g.,
        # '-ltSt' will be order by time
        # '-ltStS' will be order by size
        options = [ opt for (opt, arg) in optlist]
        for opt in options:
          if opt in ['-l', '--long']:
            _long = True
          elif opt in ['-r', '--reverse']:
            reverse = True
          elif opt in ['-t', '--timeorder']:
            timeorder = True
          elif opt in ['-n', '--numericid']:
            numericid = True  
          elif opt in ['-S', '--sizeorder']:
            sizeorder = True
          elif opt in ['-H', '--human-readable']:
            humanread = True

        if timeorder and sizeorder:
          options = [w.replace('--sizeorder','-S') for w in options]
          options = [w.replace('--human-readable','-H') for w in options]
          options.reverse()
          # The last ['-S','-t'] provided is the one we use: reverse order
          # means that the last provided has the smallest index.
          if options.index('-S') < options.index('-t'):
            timeorder = False
          else:
            sizeorder = False

        # Get path    
        if arguments:
          input_path = False
          while arguments or not input_path:
            tmparg = arguments.pop()
            # look for a non recognized option not starting with '-'
            if tmparg[0] != '-':
              path = tmparg
              input_path = True
              if path[0] != '/':
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
        dList.printListing( reverse,timeorder,sizeorder,humanread)
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
              dList.printListing( reverse,timeorder,sizeorder,humanread)      
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
  if params.long:       optstr += "l"
  if params.time:       optstr += "t"
  if params.reverse:    optstr += "r"
  if params.numericid:  optstr += "n"
  if params.size:       optstr += "S"
  if params.human:      optstr += "H"

  if optstr: optstr = "-" + optstr + " "
  # Need to check which was given the last 't' or 'S'
  # This would introduce some duplication of code :-(
  if params.long and params.time and params.size:
    short_opts = 'ltrnSH'
    long_opts = ['long','timeorder','reverse','numericid','sizeorder','human-readable']
    try:
      optlist, arguments = getopt.getopt( sys.argv[1:],short_opts,long_opts )
      options = [ opt for (opt, arg) in optlist ]
      options = [ w.replace('--size','-S') for w in options ]
      options = [ w.replace('--human-readable','-H') for w in options ]
      options.reverse()
      # The last ['-S','-t'] provided is the one we use: reverse order
      # means that the last provided has the smallest index.
      # Indeed, setTime/setSize dont has impact: the important thing is
      # to add '-S'/'-t' at the end, then do_ls takes care of the rest.
      if options.index('-S') < options.index('-t'):
        params.setTime( False )
        optstr = optstr + '-S '
      else:
        params.setSize( False )
        optstr = optstr + '-t '

    except getopt.GetoptError, e:
      print str(e)
      print fccli.do_ls.__doc__
      exit(1)

  for p in pathFromArguments( session, args ):
    print "%s:" % p
    fccli.do_ls( optstr + p )

