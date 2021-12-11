#! /usr/bin/env python

"""
configure DCommands
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC import S_OK
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

from COMDIRAC.Interfaces import (
    DConfig,
    createMinimalConfig,
    critical,
    guessProfilesFromCS,
)
from COMDIRAC.Interfaces import getDNFromProxy


class Params(object):
    def __init__(self):
        self.minimal = False
        self.guessProfile = False

    def setMinimal(self, arg):
        self.minimal = True
        return S_OK()

    def getMinimal(self):
        return self.minimal

    def setGuessProfiles(self, arg):
        self.guessProfile = True
        return S_OK()

    def getGuessProfiles(self):
        return self.guessProfile


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [options] [section[.option[=value]]]..." % Script.scriptName,
                "Arguments:",
                " without argument: display whole configuration content",
                "++ OR ++",
                " section:     display all options in section",
                "++ OR ++",
                " section.option:     display option",
                "++ OR ++",
                " section.option=value:     set option value",
            ]
        )
    )
    Script.registerSwitch(
        "m", "minimal", "verify and fill minimal configuration", params.setMinimal
    )
    Script.registerSwitch("g", "guess", "", params.setGuessProfiles)

    Script.disableCS()

    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    if params.minimal:
        createMinimalConfig()

    dconfig = DConfig()
    modified = False

    if params.getGuessProfiles():
        Script.enableCS()
        result = getDNFromProxy()
        if not result["OK"]:
            print("ERROR: %s" % result["Message"])
            DIRAC.exit(2)
        dn = result["Value"]
        result = guessProfilesFromCS(dn)
        if not result["OK"]:
            print("ERROR: %s" % result["Message"])
            DIRAC.exit(2)
        profiles = result["Value"]

        for p, pOpts in profiles.items():
            for opt, val in pOpts.items():
                modified |= dconfig.existsOrCreate(p, opt, val)

        if modified and not args:
            dconfig.write()

    if not args:
        sections = dconfig.sections()
        for s in sections:
            retVal = dconfig.get(s, None)
            if not retVal["OK"]:
                critical(retVal["Message"])

            print("[%s]" % s)
            for o, v in retVal["Value"]:
                print(o, "=", v)
            print
        DIRAC.exit(0)

    for arg in args:
        value = None
        section = None
        option = None
        if "=" in arg:
            arg, value = arg.split("=", 1)
        if "." in arg:
            section, option = arg.split(".", 1)
        else:
            section = arg

        if value != None:
            dconfig.set(section, option, value)
            modified = True
        else:
            retVal = dconfig.get(section, option)
            if not retVal["OK"]:
                critical(retVal["Message"])
            ret = retVal["Value"]
            if isinstance(ret, list):
                print("[%s]" % section)
                for o, v in ret:
                    print(o, "=", v)
            else:
                print(option, "=", ret)

    if modified:
        dconfig.write()


if __name__ == "__main__":
    main()
