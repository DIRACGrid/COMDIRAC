#! /usr/bin/env python

"""
manipulate metadata in the FileCatalog
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC import S_OK, S_ERROR

from COMDIRAC.Interfaces import critical
from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import DCatalog
from COMDIRAC.Interfaces import pathFromArgument


class DMetaCommand(object):
    def run(self, lfn, metas):
        raise NotImplementedError


class DMetaAdd(DMetaCommand):
    def __init__(self, fcClient):
        self.fcClient = fcClient

    def run(self, lfn, metas):
        metadict = {}
        for meta in metas:
            name, value = meta.split("=")
            metadict[name] = value
        result = self.fcClient.setMetadataBulk({lfn: metadict})
        if not result["OK"]:
            print("Error:", result["Message"])


class DMetaRm(DMetaCommand):
    def __init__(self, fcClient):
        self.fcClient = fcClient

    def run(self, lfn, metas):
        result = self.fcClient.removeMetadata({lfn: metas})
        if not result["OK"]:
            print("Error:", result["Message"])


class DMetaList(DMetaCommand):
    def __init__(self, catalog):
        self.catalog = catalog

    def run(self, lfn, metas):
        retVal = self.catalog.getMeta(lfn)

        if not retVal["OK"]:
            print("Error:", retVal["Message"])
            DIRAC.exit(-1)
        metadict = retVal["Value"]

        if not metas:
            for k, v in metadict.items():
                print(k + "=" + str(v))
        else:
            for meta in metas:
                if meta in metadict.keys():
                    print(meta + "=" + metadict[meta])


from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    import sys

    from COMDIRAC.Interfaces import ConfigCache

    class Params(object):
        def __init__(self):
            self.index = False
            self.listIndex = False

        def setIndex(self, arg):
            print("index", arg)
            self.index = arg
            return S_OK()

        def getIndex(self):
            return self.index

        def setListIndex(self, arg):
            self.listIndex = True

        def getListIndex(self):
            return self.listIndex

    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s -I" % Script.scriptName,
                " - list metadata indices",
                "++ OR ++",
                "  %s -i r meta..." % Script.scriptName,
                " - delete metadata index",
                "Arguments:",
                " meta:     metadata index to be deleted",
                "++ OR ++",
                "  %s -i f|d meta=(int|float|string|date)" % Script.scriptName,
                " - add metadata index for files or directories",
                "Arguments:",
                " meta=type:     metadata index to be added",
                "++ OR ++",
                "  %s add|rm|ls lfn meta[=value]..." % Script.scriptName,
                " - manipulate metadata for lfn",
                "Arguments:",
                " lfn:           path",
                " meta:          metadata (with value for add)",
                "",
                "Examples:",
                '  $ dmeta add ./some_lfn_file some_meta="some_value"',
                "  $ dmeta ls ./some_lfn_file",
                "  $ dmeta rm ./some_lfn_file some_meta",
            ]
        )
    )
    Script.registerSwitch(
        "i:", "index=", "set or remove metadata indices", params.setIndex
    )
    Script.registerSwitch(
        "I", "list-index", "list defined metadata indices", params.setListIndex
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = DCatalog()

    from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
    from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import (
        FileCatalogClientCLI,
    )

    fc = FileCatalog()
    fccli = FileCatalogClientCLI(fc)

    if params.getIndex():
        if params.getIndex() == "r":
            for meta in args:
                cmdline = "index -r %s" % meta
                # print(cmdline)
                result = fc.deleteMetadataField(meta)
        else:
            fdType = "-" + params.getIndex()
            for arg in args:
                meta, mtype = arg.split("=")
                if mtype.lower()[:3] == "int":
                    rtype = "INT"
                elif mtype.lower()[:7] == "varchar":
                    rtype = mtype
                elif mtype.lower() == "string":
                    rtype = "VARCHAR(128)"
                elif mtype.lower() == "float":
                    rtype = "FLOAT"
                elif mtype.lower() == "date":
                    rtype = "DATETIME"
                elif mtype.lower() == "metaset":
                    rtype = "MetaSet"
                else:
                    print("Error: illegal metadata type %s" % mtype)
                    DIRAC.exit(-1)
                cmdline = "index -%s %s %s" % (params.getIndex(), meta, rtype)
                # print(cmdline)
                fc.addMetadataField(meta, rtype, fdType)
        DIRAC.exit(0)

    if params.getListIndex():
        fccli.do_meta("show")
        DIRAC.exit(0)

    meta_commands = {
        "add": DMetaAdd(catalog.catalog),
        "rm": DMetaRm(catalog.catalog),
        "ls": DMetaList(catalog),
    }

    if len(args) < 2:
        print("Error: Not enough arguments provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    command = args[0]

    if command not in meta_commands.keys():
        print('Error: Unknown dmeta command "%s"' % command)
        print("%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    command = meta_commands[command]

    lfn = pathFromArgument(session, args[1])

    metas = args[2:]

    command.run(lfn, metas)


if __name__ == "__main__":
    main()
