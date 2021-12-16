#! /usr/bin/env python

"""
register DCommands session environment variables
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession

    from COMDIRAC.Interfaces import ConfigCache

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [[section.]option=value]..." % Script.scriptName,
                "Arguments:",
                '  section:     section (defaults to "session:environment")',
                "  option:      option name",
                "  value:       value to be set",
            ]
        )
    )

    configCache = ConfigCache()
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
