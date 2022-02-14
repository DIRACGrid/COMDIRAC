#! /usr/bin/env python

"""
put files in the FileCatalog (and Storage Element)

When destination SE is not specified, dput will use COMDIRAC configuration option "default_se".
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
    from COMDIRAC.Interfaces import error
    from COMDIRAC.Interfaces import critical
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import DCatalog
    from COMDIRAC.Interfaces import pathFromArgument

    from COMDIRAC.Interfaces import ConfigCache

    class Params(object):
        def __init__(self):
            self.destinationSE = False
            self.recursive = False

        def setDestinationSE(self, arg):
            self.destinationSE = arg
            return S_OK()

        def getDestinationSE(self):
            return self.destinationSE

        def setRecursive(self, arg=None):
            self.recursive = True

        def getRecursive(self):
            return self.recursive

    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] local_path[... lfn]" % Script.scriptName,
                "Arguments:",
                " local_path:   local file",
                " lfn:          file or directory entry in the file catalog",
                "",
                "Examples:",
                "  $ dput some_local_file ./some_lfn_file",
                "  $ dput local_file1 local_file2 ./some_lfn_dir/",
            ]
        )
    )
    Script.registerSwitch(
        "D:",
        "destination-se=",
        "Storage Element where to put replica",
        params.setDestinationSE,
    )
    Script.registerSwitch(
        "r", "recursive", "recursively put contents of local_path", params.setRecursive
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = DCatalog()

    from DIRAC.Interfaces.API.Dirac import Dirac

    dirac = Dirac()

    if len(args) < 1:
        error("Error: No argument provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(0)

    # local file
    localPath = args[0]

    # default lfn: same file name as localPath
    lfn = pathFromArgument(session, os.path.basename(localPath))

    pairs = [(localPath, lfn)]

    if len(args) > 1:
        # lfn provided must be last argument
        lfn = pathFromArgument(session, args[-1])
        localPaths = args[:-1]
        pairs = []

        if catalog.isDir(lfn):
            # we can accept one ore more local files
            for lp in localPaths:
                pairs.append((lp, os.path.join(lfn, os.path.basename(lp))))
        else:
            if len(localPaths) > 1:
                critical(
                    "Error: Destination LFN must be a directory when registering multiple local files"
                )

            # lfn filename replace local filename
            pairs.append((localPath, lfn))

    # destination SE
    se = params.getDestinationSE()
    if not se:
        retVal = session.getEnv("default_se", "DIRAC-USER")
        if not retVal["OK"]:
            error(retVal["Message"])
        se = retVal["Value"]

    exitCode = 0

    if params.getRecursive():
        newPairs = []
        for localPath, lfn in pairs:
            if os.path.isdir(localPath):
                for path, _subdirs, files in os.walk(localPath):
                    newLFNDir = os.path.normpath(
                        os.path.join(lfn, os.path.relpath(path, localPath))
                    )
                    for f in files:
                        pairs.append(
                            (os.path.join(path, f), os.path.join(newLFNDir, f))
                        )
            else:
                newPairs.append((localPath, lfn))
        pairs = newPairs

    for localPath, lfn in pairs:
        ret = dirac.addFile(lfn, localPath, se, printOutput=False)

        if not ret["OK"]:
            exitCode = -2
            error(lfn + ": " + ret["Message"])

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
