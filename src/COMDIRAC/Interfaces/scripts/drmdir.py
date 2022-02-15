#! /usr/bin/env python
"""
remove FileCatalog directories. Attention ! This command does not remove
directories and files on the physical storage.

Examples:
    $ drmdir ./some_lfn_directory
"""
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import createCatalog
    from COMDIRAC.Interfaces import pathFromArguments
    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.registerArgument(["Path: directory path"])
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()
    catalog = createCatalog()

    result = catalog.removeDirectory(pathFromArguments(session, args))
    if result["OK"]:
        if result["Value"]["Failed"]:
            for p in result["Value"]["Failed"]:
                print(f'ERROR - "{p}":', result["Value"]["Failed"][p])
    else:
        print("ERROR:", result["Message"])


if __name__ == "__main__":
    main()
