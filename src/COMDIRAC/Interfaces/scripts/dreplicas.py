#! /usr/bin/env python

"""
list replicas for files in the FileCatalog
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import error
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import DCatalog
    from COMDIRAC.Interfaces import pathFromArgument
    from DIRAC.Core.Utilities.ReturnValues import returnSingleResult

    from COMDIRAC.Interfaces import ConfigCache

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s lfn..." % Script.scriptName,
                "Arguments:",
                "  lfn:     logical file name",
            ]
        )
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = DCatalog()

    if len(args) < 1:
        error("No argument provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    exitCode = 0

    for arg in args:
        # lfn
        lfn = pathFromArgument(session, args[0])
        # fccli.do_replicas( lfn )
        ret = returnSingleResult(catalog.catalog.getReplicas(lfn))
        if ret["OK"]:
            replicas = ret["Value"]
            print(lfn + ":")
            for se, path in replicas.items():
                print("  ", se, path)
        else:
            error(lfn + ": " + ret["Message"])
            exitCode = -2

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
