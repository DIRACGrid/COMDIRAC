#! /usr/bin/env python
"""
print DCommands session environment variables
"""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import critical
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.registerArgument(
        "[section.]option: section:              display all options in section\n"
        "                  section.option:       display section specific option",
        mandatory=False,
    )
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

    section, option = arg.split(".") if "." in (arg := args[0]) else (None, arg)

    result = session.get(section, option) if section else session.getEnv(option)

    if not result["OK"]:
        print(critical(result["Message"]))

    print(result["Value"])


if __name__ == "__main__":
    main()
