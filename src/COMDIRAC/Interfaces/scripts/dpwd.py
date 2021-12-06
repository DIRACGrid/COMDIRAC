#! /usr/bin/env python

"""
print DCommands working directory
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
                "  %s [options]" % Script.scriptName,
            ]
        )
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    session = DSession()

    args = Script.getPositionalArgs()

    ret = session.getCwd()

    print(ret)


if __name__ == "__main__":
    main()
