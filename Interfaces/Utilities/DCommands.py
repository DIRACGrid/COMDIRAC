
from types import ListType, DictType
import json

import DIRAC
from DIRAC  import S_OK, S_ERROR

def listFormatPretty( summaries, headers = None, sortKeys = None ):
  headerWidths = {}
  for i, c in enumerate( headers ):
    headerWidths[i] = len( c )

  for s in summaries:
    for i, v in enumerate( s ):
      l = len ( str( v ) )
      if l > headerWidths[i]:
        headerWidths[i] = l

  ret = ""
  for i, header in enumerate( headers ):
    ret += "{field:^{width}} ".format( field = header, width = headerWidths[i] )
  ret += "\n"
  for i, header in enumerate( headers ):
    ret += "{field} ".format( field = "-" * headerWidths[i] )
  ret += "\n"

  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    for i, header in enumerate( headers ):
      ret += "{field:^{width}} ".format( field = s[i], width = headerWidths[i] )
    ret += "\n"

  return ret

def listFormatCSV( summaries, headers = None, sortKeys = None ):
  ret = ""
  for header in headers:
    ret += header + ","
  ret += "\n"

  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    for i, header in enumerate( headers ):
      ret += str( s[i] ) + ","
    ret += "\n"
  return ret

def listFormatJSON( summaries, headers = None, sortKeys = None ):
  l = []
  if not sortKeys:
    sortKeys = map( lambda e: ( None, e ), range( len( summaries ) ) )

  for _k, i in sortKeys:
    s = summaries[i]
    d = {}
    for j, header in enumerate( headers ):
      d[header] = s[j]
    l.append( d )

  return json.dumps( l )

class ArrayFormatter:
  fmts = {"csv" : listFormatCSV, "pretty" : listFormatPretty, "json" : listFormatJSON}

  def __init__( self, outputFormat ):
    self.outputFormat = outputFormat

  def listFormat( self, list_, headers, sort = None ):
    if self.outputFormat not in self.fmts:
      return S_ERROR( "ArrayFormatter: Output format not supported: %s not in %s" %
                      ( self.outputFormat, self.fmts.keys() ) )

    if headers is None:
      if len( list_ ) == 0:
        return S_OK( "" )
      headers = range( list_ )

    sortKeys = None
    if sort is not None:
      sortKeys = []
      for i, s in enumerate( list_ ):
        sortKeys.append( ( s[sort], i ) )
      sortKeys.sort()

    return self.fmts[self.outputFormat]( list_, headers, sortKeys )

  def dictFormat( self, dict_, headers = None, sort = None ):
    if headers is None: headers = dict_.keys()
    list_ = []
    for v in dict_.values():
      row = []
      for h in headers:
        row.append( v[h] )
      list_.append( row )

    if sort is not None:
      sort = headers.index( sort )

    return self.listFormat( list_, headers, sort )
