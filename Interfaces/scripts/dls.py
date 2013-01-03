#! /usr/bin/env python
########################################################################
# $HeadURL: $
########################################################################
__RCSID__   = "$Id:  $"

import os, sys
from DIRAC import S_OK
from DIRAC.Core.Base import Script 

#######################################################################
#
# Prepare the command call, switches and docs

Script.setUsageMessage("""
Show file or list the contents of a FileCatalog directory

Usage:
   ls <options> <path>
""")

class Parameters:

  longOutput = False
  sortTime = False
  reverse = False
  numericID = False
  
  def setLongOutput( self, arg ):
    self.longOutput = True
    return S_OK()
  
  def setSortTime( self, arg ):
    self.sortTime = True 
    return S_OK()
    
  def setReverse( self, arg ):
    self.reverse = True
    return S_OK()
    
  def setNumericID( self, arg ):
    self.numericID = True
    return S_OK()

params = Parameters()

Script.registerSwitch( "l", "", "Long listing", params.setLongOutput )
Script.registerSwitch( "t", "", "Sort by time", params.setSortTime )
Script.registerSwitch( "r", "", "Reverse sorting", params.setReverse )
Script.registerSwitch( "n", "", "Show numerical user and group ids", params.setNumericID )

Script.parseCommandLine()
args = Script.getPositionalArgs()

if len( args ) == 0:
  Script.showHelp()
  sys.exit( -1 )

############################################################################
#
# Imports depending on the configuration parsing

from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import DirectoryListing

############################################################################
#
#  Do the work now

path = args[0]
if path[-1] == '/' and path != '/':
  path = path[:-1]

fc = FileCatalog()

# Check if the target path is a file
result =  fc.isFile(path)          
if not result['OK']:
  print "Error: can not find path"
  sys.exit(1)
elif path in result['Value']['Successful'] and result['Value']['Successful'][path]:
  result = fc.getFileMetadata(path)      
  dList = DirectoryListing()
  fileDict = result['Value']['Successful'][path]
  dList.addFile( os.path.basename(path), fileDict, params.numericID )
  dList.printListing( params.reverse, params.sortTime )
  sys.exit()     

# Get directory contents now
try:
  result =  fc.listDirectory( path, params.longOutput )                     
  dList = DirectoryListing()
  if result['OK']:
    if result['Value']['Successful']:
      for entry in result['Value']['Successful'][path]['Files']:
        fname = entry.split('/')[-1]
        # print entry, fname
        # fname = entry.replace(self.cwd,'').replace('/','')
        if params.longOutput:
          fileDict = result['Value']['Successful'][path]['Files'][entry]['MetaData']
          if fileDict:
            dList.addFile( fname, fileDict, params.numericID )
        else:  
          dList.addSimpleFile(fname)
      for entry in result['Value']['Successful'][path]['SubDirs']:
        dname = entry.split('/')[-1]
        # print entry, dname
        # dname = entry.replace(self.cwd,'').replace('/','')  
        if params.longOutput:
          dirDict = result['Value']['Successful'][path]['SubDirs'][entry]
          if dirDict:
            dList.addDirectory( dname, dirDict, params.numericID )
        else:    
          dList.addSimpleFile(dname)
      for entry in result['Value']['Successful'][path]['Links']:
        pass
          
      if params.longOutput:
        dList.printListing( params.reverse, params.sortTime )      
      else:
        dList.printOrdered()
  else:
    print "Error:", result['Message']
except Exception, x:
  print "Exception:", str(x)
