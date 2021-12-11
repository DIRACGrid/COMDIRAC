"""
  Retrieve input sandbox for a DIRAC job
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

import os
import pprint


class Params(object):
    def __init__(self):
        self.outputDir = None
        self.verbose = False
        self.downloadJDL = False
        self.inputSandbox = False
        self.jobGroup = []
        self.inputFile = None

    def setOutputDir(self, arg=None):
        self.outputDir = arg

    def getOutputDir(self):
        return self.outputDir

    def setDownloadJDL(self, arg=None):
        self.downloadJDL = True

    def getDownloadJDL(self):
        return self.downloadJDL

    def setInputSandbox(self, arg=None):
        self.inputSandbox = True

    def getInputSandbox(self):
        return self.inputSandbox

    def setVerbose(self, arg=None):
        self.verbose = True

    def getVerbose(self):
        return self.verbose

    def setJobGroup(self, arg=None):
        if arg:
            self.jobGroup.append(arg)

    def getJobGroup(self):
        return self.jobGroup

    def setInputFile(self, arg=None):
        self.inputFile = arg

    def getInputFile(self):
        return self.inputFile


@Script()
def main():
    from COMDIRAC.Interfaces import ConfigCache

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
        "D:", "OutputDir=", "destination directory", params.setOutputDir
    )
    Script.registerSwitch(
        "j", "JDL", "download job JDL instead of input sandbox", params.setDownloadJDL
    )
    Script.registerSwitch(
        "",
        "Sandbox",
        "donwload input sandbox, even if JDL was required",
        params.setInputSandbox,
    )
    Script.registerSwitch("v", "verbose", "verbose output", params.setVerbose)
    Script.registerSwitch(
        "g:", "JobGroup=", "Get output for jobs in the given group", params.setJobGroup
    )
    Script.registerSwitch(
        "i:", "input-file=", "read JobIDs from file", params.setInputFile
    )

    configCache = ConfigCache()
    Script.parseCommandLine(ignoreErrors=True)
    configCache.cacheConfig()

    args = Script.getPositionalArgs()

    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Core.Utilities.Time import toString, date, day

    dirac = Dirac()
    exitCode = 0

    if args:
        # handle comma separated list of JobIDs
        newargs = []
        for arg in args:
            newargs += arg.split(",")
        args = newargs

    if params.getInputFile() != None:
        with open(params.getInputFile(), "r") as f:
            for l in f.readlines():
                args += l.split(",")

    for jobGroup in params.getJobGroup():
        jobDate = toString(date() - 30 * day)

        # Choose jobs no more than 30 days old
        result = dirac.selectJobs(jobGroup=jobGroup, date=jobDate)
        if not result["OK"]:
            if not "No jobs selected" in result["Message"]:
                print("Error:", result["Message"])
                exitCode = 2
        else:
            args += result["Value"]

    jobs = []

    outputDir = params.getOutputDir() or os.path.curdir

    for arg in args:
        if os.path.isdir(os.path.join(outputDir, "InputSandbox%s" % arg)):
            print(
                "Input for job %s already retrieved, remove the output directory to redownload"
                % arg
            )
        else:
            jobs.append(arg)

    if jobs:
        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)

        errors = []
        inputs = {}
        for job in jobs:
            destinationDir = os.path.join(outputDir, "InputSandbox%s" % job)

            inputs[job] = {"destinationDir": destinationDir}

            if params.getInputSandbox() or not params.getDownloadJDL():

                result = dirac.getInputSandbox(job, outputDir=outputDir)
                if result["OK"]:
                    inputs[job]["isb"] = destinationDir
                else:
                    errors.append(result["Message"])
                    exitCode = 2

            if params.getDownloadJDL():
                result = dirac.getJobJDL(job, printOutput=False)
                if result["OK"]:
                    if not os.path.exists(destinationDir):
                        os.makedirs(destinationDir)
                    jdl = pprint.pformat(result["Value"])
                    with open(os.path.join(destinationDir, "%s.jdl" % job), "w") as f:
                        f.write(jdl)
                        f.close()

                    inputs[job]["jdl"] = jdl
                else:
                    errors.append(result["Message"])
                    exitCode = 2

        for error in errors:
            print("ERROR: %s" % error)

        if params.getVerbose():
            for j, d in inputs.items():
                if "isb" in d:
                    print("%s: InputSandbox" % j, d["isb"])
                if "jdl" in d:
                    print("%s: JDL" % j, d["jdl"])
    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
