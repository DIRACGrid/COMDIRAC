#! /usr/bin/env python

"""
  Retrieve status of DIRAC jobs
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__RCSID__ = "$Id$"

from signal import signal, SIGPIPE, SIG_DFL
import six

from COMDIRAC.Interfaces import ConfigCache
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC import S_OK
from DIRAC.Core.Utilities.Time import toString, date, day

from COMDIRAC.Interfaces.Utilities.DCommands import ArrayFormatter

# TODO: how to import job states from JobDB in client installation (lacks MySQLdb module)?
# from DIRAC.WorkloadManagementSystem.DB.JobDB import JOB_STATES, JOB_FINAL_STATES
JOB_STATES = [
    "Received",
    "Checking",
    "Staging",
    "Waiting",
    "Matched",
    "Running",
    "Stalled",
    "Done",
    "Completed",
    "Failed",
]
JOB_FINAL_STATES = ["Done", "Completed", "Failed"]

# broken pipe default behaviour
signal(SIGPIPE, SIG_DFL)


def selectJobs(owner, date, jobGroup, jobName):
    conditions = {"Owner": owner}
    if jobGroup:
        conditions["JobGroup"] = jobGroup
    if jobName:
        conditions["JobName"] = jobName

    monitoring = RPCClient("WorkloadManagement/JobMonitoring")
    result = monitoring.getJobs(conditions, date)

    return result


def getJobSummary(jobs):
    if not jobs:
        return S_OK({})
    monitoring = RPCClient("WorkloadManagement/JobMonitoring")
    result = monitoring.getJobsSummary(jobs)
    if not result["OK"]:
        return result

    if isinstance(result["Value"], six.string_types):
        try:
            jobSummary = eval(result["Value"])
        except:
            return S_ERROR("Problem while converting result from job monitoring")
    else:
        jobSummary = result["Value"]
    return S_OK(jobSummary)


def chunks(l, n):
    return [l[i : i + n] for i in range(0, len(l), n)]


EXTRA_DISPLAY_COLUMNS = [
    "JobType",
    "ApplicationStatus",
    "StartExecTime",
    "EndExecTime",
    "CPUTime",
]

DEFAULT_DISPLAY_COLUMNS = [
    "Owner",
    "JobName",
    "OwnerGroup",
    "JobGroup",
    "Site",
    "Status",
    "MinorStatus",
    "SubmissionTime",
]


class Params(object):
    def __init__(self):
        self.__session = None
        self.user = None
        self.status = map(lambda e: e.lower(), set(JOB_STATES) - set(JOB_FINAL_STATES))
        self.fmt = "pretty"
        self.jobDate = 10
        self.fields = DEFAULT_DISPLAY_COLUMNS
        self.jobGroup = None
        self.jobName = None
        self.inputFile = None

    def setSession(self, session):
        self.__session = session
        customFields = session.getEnv("dstat_fields", "")["Value"]
        if customFields:
            self.fields = customFields.split(",")
        return S_OK()

    def setUser(self, arg=None):
        self.user = arg
        return S_OK()

    def getUser(self):
        return self.user

    def setStatus(self, arg=None):
        self.status = arg.lower().split(",")
        return S_OK()

    def setStatusAll(self, arg=None):
        self.status = map(lambda e: e.lower(), JOB_STATES)
        return S_OK()

    def getStatus(self):
        return self.status

    def setFmt(self, arg=None):
        self.fmt = arg.lower()
        return S_OK()

    def getFmt(self):
        return self.fmt

    def setJobDate(self, arg=None):
        self.jobDate = int(arg)
        return S_OK()

    def getJobDate(self):
        return self.jobDate

    def setFields(self, arg=None):
        self.fields = arg.split(",")
        return S_OK()

    def getFields(self):
        return self.fields

    def setJobGroup(self, arg=None):
        self.jobGroup = arg
        return S_OK()

    def getJobGroup(self):
        return self.jobGroup

    def setJobName(self, arg=None):
        self.jobName = arg
        return S_OK()

    def getJobName(self):
        return self.jobName

    def setInputFile(self, arg=None):
        self.inputFile = arg
        return S_OK()

    def getInputFile(self):
        return self.inputFile


@Script()
def main():
    params = Params()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__.split("\n")[1],
                "Usage:",
                "  %s [option|cfgfile] " % Script.scriptName,
                "Arguments:",
            ]
        )
    )
    Script.registerSwitch("u:", "User=", "job owner", params.setUser)
    Script.registerSwitch(
        "S:",
        "Status=",
        "select job by status (comma separated list of statuses in: %s)"
        % ",".join(JOB_STATES),
        params.setStatus,
    )
    Script.registerSwitch(
        "a", "StatusAll", "display jobs of any status", params.setStatusAll
    )
    Script.registerSwitch(
        "g:", "JobGroup=", "select job by job group", params.setJobGroup
    )
    Script.registerSwitch("n:", "JobName=", "select job by job name", params.setJobName)
    Script.registerSwitch(
        "f:", "Fmt=", "display format (pretty, csv, json)", params.setFmt
    )
    Script.registerSwitch(
        "D:", "JobDate=", "age of jobs to display (in days)", params.setJobDate
    )
    Script.registerSwitch(
        "F:",
        "Fields=",
        "display list of job fields (comma separated list of fields. e.g. %s)"
        % ",".join(DEFAULT_DISPLAY_COLUMNS + EXTRA_DISPLAY_COLUMNS),
        params.setFields,
    )
    Script.registerSwitch(
        "i:", "input-file=", "read JobIDs from file", params.setInputFile
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    import DIRAC
    from DIRAC import S_OK, S_ERROR
    from DIRAC import exit as DIRACExit
    from DIRAC.Core.DISET.RPCClient import RPCClient
    from COMDIRAC.Interfaces import DSession

    session = DSession()
    params.setSession(session)

    exitCode = 0

    if args:
        # handle comma separated list of JobIDs
        newargs = []
        for arg in args:
            newargs += arg.split(",")
        args = newargs

    jobs = args

    if params.getInputFile() != None:
        with open(params.getInputFile(), "r") as f:
            for l in f.readlines():
                jobs += l.split(",")

    if not jobs:
        # time interval
        jobDate = toString(date() - params.getJobDate() * day)

        # job owner
        userName = params.getUser()
        if userName is None:
            result = session.getUserName()
            if result["OK"]:
                userName = result["Value"]
        elif userName == "*" or userName.lower() == "__all__":
            # jobs from all users
            userName = None

        result = selectJobs(
            owner=userName,
            date=jobDate,
            jobGroup=params.getJobGroup(),
            jobName=params.getJobName(),
        )

        if not result["OK"]:
            print("Error:", result["Message"])
            DIRACExit(-1)

        jobs = result["Value"]

    try:
        jobs = [int(job) for job in jobs]
    except Exception as x:
        print("Expected integer for jobID")
        exitCode = 2
        DIRAC.exit(exitCode)

    summaries = {}
    statuses = params.getStatus()

    # split summary requests in chunks of a reasonable size (saves memory)
    for chunk in chunks(jobs, 1000):
        result = getJobSummary(chunk)
        if not result["OK"]:
            print("ERROR: %s" % result["Message"])
            DIRAC.exit(2)

        # filter on job statuses
        if "all" in statuses:
            summaries = result["Value"]
        else:
            for j, s in result["Value"].items():
                if s["Status"].lower() in statuses:
                    summaries[j] = s

    for s in summaries.values():
        s["JobID"] = int(s["JobID"])

    af = ArrayFormatter(params.getFmt())

    print(af.dictFormat(summaries, ["JobID"] + params.getFields(), sort="JobID"))

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
