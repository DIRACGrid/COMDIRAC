#! /usr/bin/env python
"""
register DCommands session environment variables
"""
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.registerArgument(
        '[section.]option=value: section: section (defaults to "session:environment")\n'
        "                        option:  option name\n"
        "                        value:   value to be set",
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

        arg, value = arg.split("=", 1)
        if "." in arg:
            section, option = arg.split(".", 1)
        else:
            option = arg

        if section:
            session.set(section, option, value)
        else:
            session.setEnv(option, value)
        modified = True

    if modified:
        session.write()


if __name__ == "__main__":
    main()
