#! /usr/bin/env python
"""
print DCommands working directory
"""
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from COMDIRAC.Interfaces import DSession
    from COMDIRAC.Interfaces import ConfigCache

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    print(DSession().getCwd())


if __name__ == "__main__":
    main()
