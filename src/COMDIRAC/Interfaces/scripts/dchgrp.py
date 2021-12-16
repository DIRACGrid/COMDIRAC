#! /usr/bin/env python
########################################################################
# $HeadURL$
########################################################################

"""
Change file owner's group
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC import S_OK


class Params(object):
    def __init__(self):
        self.recursive = False

    def setRecursive(self, opt):
        self.recursive = True
        return S_OK()

    def getRecursive(self):
        return self.recursive


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] group Path..." % Script.scriptName,
                "Arguments:",
                "  group:    new group name",
                "  Path:     path to file",
                "",
                "Examples:",
                "  $ dchown atsareg ././some_lfn_file",
                "  $ dchown -R pgay ./",
            ]
        )
    )
    Script.registerSwitch("R", "recursive", "recursive", params.setRecursive)

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    import DIRAC
    from DIRAC import gLogger
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import pathFromArgument

    session = DSession()

    if len(args) < 2:
        print("Error: not enough arguments provided\n%s:" % Script.scriptName)
        Script.showHelp()
        DIRAC.exit(-1)

    group = args[0]

    lfns = []
    for path in args[1:]:
        lfns.append(pathFromArgument(session, path))

    from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

    fc = FileCatalog()

    for lfn in lfns:
        try:
            pathDict = {lfn: group}
            result = fc.changePathGroup(pathDict, params.recursive)
            if not result["OK"]:
                gLogger.error("Error:", result["Message"])
                break
            if lfn in result["Value"]["Failed"]:
                gLogger.error("Error:", result["Value"]["Failed"][lfn])
        except Exception as x:
            print("Exception:", str(x))


if __name__ == "__main__":
    main()
