#! /usr/bin/env python

"""
remove DCommands session environment variables
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from COMDIRAC.Interfaces import critical

from COMDIRAC.Interfaces import DSession

from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


@Script()
def main():
    from COMDIRAC.Interfaces import ConfigCache

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [[section.]option]..." % Script.scriptName,
                "Arguments:",
                '  section:     section (default: "session:environment")',
                "  option:      option name",
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
