#! /usr/bin/env python
"""
create a directory in the FileCatalog

Examples:
    $ dmkdir ./some_lfn_dir
"""
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import createCatalog
    from COMDIRAC.Interfaces import pathFromArguments

    configCache = ConfigCache()
    Script.registerArgument(["Path: path to new directory"])
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = createCatalog()

    result = catalog.createDirectory(pathFromArguments(session, args))
    if result["OK"]:
        if result["Value"]["Failed"]:
            for p in result["Value"]["Failed"]:
                print(f'ERROR - "{p}":', result["Value"]["Failed"][p])
    else:
        print("ERROR:", result["Message"])


if __name__ == "__main__":
    main()
