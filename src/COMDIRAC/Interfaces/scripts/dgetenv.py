#! /usr/bin/env python

"""
print DCommands session environment variables
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import critical

    from COMDIRAC.Interfaces import DSession

    from COMDIRAC.Interfaces import ConfigCache

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [[section.]option]" % Script.scriptName,
                "Arguments:",
                " section:     display all options in section",
                "++ OR ++",
                " section.option:     display section specific option",
            ]
        )
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()

    if not args:
        retVal = session.listEnv()
        if not retVal["OK"]:
            print("Error:", retVal["Message"])
            DIRAC.exit(-1)
        for o, v in retVal["Value"]:
            print(o + "=" + v)
        DIRAC.exit(0)

    arg = args[0]

    section = None
    option = None

    if "." in arg:
        section, option = arg.split(".")
    else:
        option = arg

    ret = None
    if section:
        ret = session.get(section, option)
    else:
        ret = session.getEnv(option)

    if not ret["OK"]:
        print(critical(ret["Message"]))

    print(ret["Value"])


if __name__ == "__main__":
    main()
