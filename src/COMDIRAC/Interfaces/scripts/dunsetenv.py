#! /usr/bin/env python
"""
Remove DCommands session environment variables
"""
from COMDIRAC.Interfaces import DSession
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.registerArgument(
        '[section.]option=value: section: section (defaults to "session:environment")\n'
        "                        option:  option name",
        mandatory=False,
    )
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    session = DSession()

    modified = False
    for arg in args:
        section = None
        option = None

        if "." in arg:
            section, option = arg.split(".")
        else:
            option = arg

        if section:
            session.remove(section, option)
        else:
            session.unsetEnv(option)

        modified = True

    if modified:
        session.write()


if __name__ == "__main__":
    main()
