#! /usr/bin/env python

"""
remove FileCatalog directories. Attention ! This command does not remove
directories and files on the physical storage.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import createCatalog
    from COMDIRAC.Interfaces import pathFromArguments

    from COMDIRAC.Interfaces import ConfigCache

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [Path]..." % Script.scriptName,
                "Arguments:",
                "  Path:     directory path",
                "",
                "Examples:",
                "  $ drmdir ./some_lfn_directory",
            ]
        )
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()

    if len(args) < 1:
        print("Error: No argument provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    catalog = createCatalog()

    result = catalog.removeDirectory(pathFromArguments(session, args))
    if result["OK"]:
        if result["Value"]["Failed"]:
            for p in result["Value"]["Failed"]:
                print('ERROR - "%s": %s' % (p, result["Value"]["Failed"][p]))
    else:
        print("ERROR: %s" % result["Message"])


if __name__ == "__main__":
    main()
