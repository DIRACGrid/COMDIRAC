#! /usr/bin/env python
"""
  Kill or delete DIRAC job
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__RCSID__ = "$Id$"

import DIRAC
from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from COMDIRAC.Interfaces import DSession


class Params(object):
    def __init__(self):
        self.delete = False
        self.selectAll = False
        self.verbose = False

    def setDelete(self, arg=None):
        self.delete = True

    def getDelete(self):
        return self.delete

    def setSelectAll(self, arg=None):
        self.selectAll = True

    def getSelectAll(self):
        return self.selectAll

    def setVerbose(self, arg=None):
        self.verbose = True

    def getVerbose(self):
        return self.verbose


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [option|cfgfile] JobID ..." % Script.scriptName,
                "Arguments:",
                "  JobID: a DIRAC job identifier",
            ]
        )
    )
    Script.registerSwitch("D", "delete", "delete job", params.setDelete)
    Script.registerSwitch("a", "all", "select all jobs", params.setSelectAll)
    Script.registerSwitch("v", "verbose", "verbose output", params.setVerbose)

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    exitCode = 0

    from DIRAC.WorkloadManagementSystem.Client.WMSClient import WMSClient
    from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import (
        JobMonitoringClient,
    )

    wmsClient = WMSClient()

    jobs = args

    if params.getSelectAll():
        session = DSession()
        result = session.getUserName()
        if result["OK"]:
            userName = result["Value"]

            monitoring = JobMonitoringClient()
            result = monitoring.getJobs({"Owner": userName})
            if not result["OK"]:
                print("ERROR:", result["Message"])
            else:
                jobs += map(int, result["Value"])
        else:
            print("ERROR:", result["Message"])

    errors = []
    for job in jobs:
        result = None
        if params.delete:
            result = wmsClient.deleteJob(job)
        else:
            result = wmsClient.killJob(job)
        if not result["OK"]:
            errors.append(result["Message"])
            exitCode = 2
        elif params.getVerbose():
            action = "killed"
            if params.getDelete():
                action = "deleted"
            print("%s job %s" % (action, job))

    for error in errors:
        print("ERROR: %s" % error)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
