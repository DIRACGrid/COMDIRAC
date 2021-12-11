#! /usr/bin/env python

"""
initialize DCommands session
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import DIRAC
from COMDIRAC.Interfaces import DConfig, DSession, critical
from COMDIRAC.Interfaces.Utilities.DCommands import sessionFromProxy
from COMDIRAC.Interfaces import ConfigCache
from COMDIRAC.Interfaces.Utilities.DConfigCache import check_lcg_import
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
import DIRAC.Core.Security.ProxyInfo as ProxyInfo


class Params(object):
    def __init__(self):
        self.fromProxy = False
        self.destroy = False

    def setFromProxy(self, arg):
        self.fromProxy = True

    def getFromProxy(self):
        return self.fromProxy

    def setDestroy(self, arg):
        self.destroy = True

    def getDestroy(self):
        return self.destroy


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] [profile_name]" % Script.scriptName,
                "Arguments:",
                " profile_name:     existing profile section in DCommands config",
            ]
        )
    )
    Script.registerSwitch(
        "p", "fromProxy", "build session from existing proxy", params.setFromProxy
    )
    Script.registerSwitch(
        "D", "destroy", "destroy session information", params.setDestroy
    )

    Script.disableCS()

    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    profile = None
    if len(args):
        profile = args[0]

    if params.destroy:
        session = DSession()
        os.unlink(session.configPath)
        DIRAC.exit(0)

    session = None
    if params.fromProxy:
        retVal = Script.enableCS()
        ConfigCache(forceRefresh=True).cacheConfig()

        if not retVal["OK"]:
            critical(retVal["Message"])

        session = sessionFromProxy()
    else:
        session = DSession(profile)

    if not session:
        print("Error: Session couldn't be initialized")
        DIRAC.exit(-1)

    session.write()

    try:
        session.checkProxyOrInit()
    except Exception as e:
        print("Error: %s", e)
        DIRAC.exit(-1)

    retVal = session.proxyInfo()
    if not retVal["OK"]:
        print(retVal["Message"])
        DIRAC.exit(-1)

    print(ProxyInfo.formatProxyInfoAsString(retVal["Value"]))

    if not check_lcg_import():
        print("")
        print(
            "Warning: Couldn't import module lcg_utils. SRM file transfers will be proxied if possible."
        )


if __name__ == "__main__":
    main()
