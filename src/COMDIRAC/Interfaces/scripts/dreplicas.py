#! /usr/bin/env python
"""
Print list replicas for files in the FileCatalog
"""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import error
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import DCatalog
    from COMDIRAC.Interfaces import pathFromArgument
    from DIRAC.Core.Utilities.ReturnValues import returnSingleResult

    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.registerArgument(["lfn: logical file name"])
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = DCatalog()

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
