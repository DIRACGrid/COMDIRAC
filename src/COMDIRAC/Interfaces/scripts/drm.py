#! /usr/bin/env python

"""
remove files from the FileCatalog (and all replicas from Storage Elements)
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import DIRAC
from DIRAC import S_OK
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import critical
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import DCatalog

    from COMDIRAC.Interfaces import pathFromArgument

    from COMDIRAC.Interfaces import ConfigCache

    lfnFileName = ""

    def setLfnFileName(arg):
        global lfnFileName
        lfnFileName = arg
        return S_OK()

    targetSE = ""

    def setSE(arg):
        global targetSE
        targetSE = arg
        return S_OK()

    rmDirFlag = False

    def setDirFlag(arg):
        global rmDirFlag
        rmDirFlag = True
        return S_OK()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] [lfn]..." % Script.scriptName,
                "Arguments:",
                "  lfn:     logical file name",
                "",
                "Examples:",
                "  $ drm ./some_lfn_file",
            ]
        )
    )

    Script.registerSwitch(
        "F:", "lfnFile=", "file containing a list of LFNs", setLfnFileName
    )
    Script.registerSwitch(
        "D:", "destination-se=", "Storage Element from where to remove replica", setSE
    )
    Script.registerSwitch("r", "", "remove directory recursively", setDirFlag)

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = DCatalog()

    if len(args) < 1 and not lfnFileName:
        print("Error: No argument provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    lfns = set()
    for path in args:
        lfns.add(pathFromArgument(session, path))

    if lfnFileName:
        if not os.path.exists(lfnFileName):
            print("Error: non-existent file %s:" % lfnFileName)
            DIRAC.exit(-1)
        lfnFile = open(lfnFileName, "r")
        lfnList = lfnFile.readlines()
        lfnSet = set([pathFromArgument(session, lfn.strip()) for lfn in lfnList if lfn])
        lfns.update(lfnSet)

    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC import gLogger
    from DIRAC.Core.Utilities.ReturnValues import returnSingleResult
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager

    dirac = Dirac()
    dm = DataManager()

    nLfns = len(lfns)
    if nLfns > 1:
        gLogger.notice("Removing %d objects" % nLfns)

    exitCode = 0
    goodCounter = 0
    badCounter = 0
    failed = {}
    for lfn in lfns:
        if rmDirFlag and not catalog.isFile(lfn):
            result = returnSingleResult(dm.cleanLogicalDirectory(lfn))
            if result["OK"]:
                goodCounter += 1
            else:
                print("ERROR: %s" % result["Message"])
                badCounter += 1
                exitCode = 3
        else:
            if targetSE:
                result = returnSingleResult(
                    dirac.removeReplica(lfn, targetSE, printOutput=False)
                )
            else:
                result = returnSingleResult(dirac.removeFile(lfn, printOutput=False))
            if not result["OK"]:
                if "No such file or directory" == result["Message"]:
                    gLogger.notice("%s: no such file" % lfn)
                else:
                    gLogger.error("ERROR %s: %s" % (lfn, result["Message"]))
                    badCounter += 1
                    exitCode = 2
            else:
                goodCounter += 1
                if goodCounter % 10 == 0:
                    gLogger.notice("%d files removed" % goodCounter)
                    if badCounter:
                        gLogger.notice("%d files failed removal" % badCounter)

    gLogger.notice("\n%d object(s) removed in total" % goodCounter)
    if badCounter:
        gLogger.notice("%d object(s) failed removal in total" % badCounter)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
