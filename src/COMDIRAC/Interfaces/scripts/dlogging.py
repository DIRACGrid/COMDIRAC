"""
  Retrieve logging information for a DIRAC job
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script


class Params(object):
    def __init__(self):
        self.fmt = "pretty"

    def setFmt(self, arg=None):
        self.fmt = arg.lower()

    def getFmt(self):
        return self.fmt


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [option|cfgfile] ... JobID ..." % Script.scriptName,
                "Arguments:",
                "  JobID:    DIRAC Job ID",
            ]
        )
    )
    Script.registerSwitch(
        "f:", "Fmt=", "display format (pretty, csv, json)", params.setFmt
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import (
        JobMonitoringClient,
    )
    from COMDIRAC.Interfaces.Utilities.DCommands import ArrayFormatter

    exitCode = 0

    jobs = map(int, args)

    monitoring = JobMonitoringClient()
    af = ArrayFormatter(params.getFmt())
    headers = ["Status", "MinorStatus", "ApplicationStatus", "Time", "Source"]
    errors = []
    for job in jobs:
        result = monitoring.getJobLoggingInfo(job)
        if result["OK"]:
            print(af.listFormat(result["Value"], headers, sort=headers.index("Time")))
        else:
            errors.append(result["Message"])
            exitCode = 2

    for error in errors:
        print("ERROR: %s" % error)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
