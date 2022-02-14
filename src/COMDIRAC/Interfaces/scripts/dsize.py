#! /usr/bin/env python

"""
print FileCatalog file or directory disk usage
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from signal import signal, SIGPIPE, SIG_DFL

from DIRAC import S_OK
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import createCatalog
    from COMDIRAC.Interfaces import pathFromArguments

    from COMDIRAC.Interfaces import ConfigCache

    # broken pipe default behaviour
    signal(SIGPIPE, SIG_DFL)

    class Params(object):
        def __init__(self):
            self.long = False
            self.rawFiles = False

        def setLong(self, arg=None):
            self.long = True
            return S_OK()

        def getLong(self):
            return self.long

        def setRawFiles(self, arg=None):
            self.rawFiles = True
            return S_OK()

        def getRawFiles(self):
            return self.rawFiles

    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] [path]" % Script.scriptName,
                "Arguments:",
                " path:     file/directory path",
            ]
        )
    )
    Script.registerSwitch("l", "long", "detailled listing", params.setLong)
    Script.registerSwitch("f", "raw-files", "reverse sort order", params.setRawFiles)

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import (
        FileCatalogClientCLI,
    )

    session = DSession()

    fccli = FileCatalogClientCLI(createCatalog())

    optstr = ""
    if params.long:
        optstr += "-l "
    if params.rawFiles:
        optstr += "-f "

    for p in pathFromArguments(session, args):
        fccli.do_size(optstr + p)


if __name__ == "__main__":
    main()
