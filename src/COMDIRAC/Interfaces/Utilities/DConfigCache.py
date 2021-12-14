from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import stat
import time
import re

try:
    import cPickle as pickle  # python 2
except ImportError:
    import pickle  # python 3

from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData


def check_lcg_import():
    try:
        import lcg_util
    except ImportError:
        return False

    return True


def proxy_lcg_protocols_if_missing():
    if not check_lcg_import():
        # if not available, mark LCG protocols to be proxied
        gConfigurationData.setOptionInCFG(
            "/LocalSite/StorageElements/ProxyProtocols", "srm"
        )


class ConfigCache(object):
    @classmethod
    def cacheFilePrefix(cls):
        return "DSession.configCache"

    cacheDir = "/tmp"

    def __init__(self, forceRefresh=False):
        self.newConfig = True
        self.configCacheLifetime = 600.0  # ten minutes

        if "DCOMMANDS_PPID" in os.environ:
            self.pid = int(os.environ["DCOMMANDS_PPID"])
        else:
            self.pid = os.getppid()

        self.configCacheName = os.path.join(
            self.cacheDir, self.cacheFilePrefix() + ".%d.%d" % (os.getuid(), self.pid)
        )

        if not forceRefresh:
            self.loadConfig()

    def __cleanCacheDirectory(self):
        def pid_exists(pid):
            try:
                os.kill(pid, 0)
            except OSError as _err:
                return False
            return True

        cachePat = "^" + self.cacheFilePrefix() + "\.%s\.(?P<pid>[0-9]+)$" % os.getuid()
        cacheRe = re.compile(cachePat)
        for f in os.listdir(self.cacheDir):
            m = cacheRe.match(f)
            if m is not None:
                pid = int(m.group("pid"))

                path = os.path.join(self.cacheDir, f)
                # delete session files for non running processes
                if not pid_exists(pid) and os.access(path, os.W_OK):
                    # print("remove old session file", path)
                    os.unlink(path)
                else:
                    # print("keep session file", path)
                    pass

    def loadConfig(self):
        self.newConfig = True

        if os.path.isfile(self.configCacheName):
            cacheStamp = os.stat(self.configCacheName).st_mtime
            # print(time.time() - cacheStamp, self.configCacheLifetime, time.time() - cacheStamp <= self.configCacheLifetime)
            if time.time() - cacheStamp <= self.configCacheLifetime:
                Script.disableCS()
                self.newConfig = False
                # print('use cached config')

    def cacheConfig(self):
        if self.newConfig:
            self.__cleanCacheDirectory()

            proxy_lcg_protocols_if_missing()

            with open(self.configCacheName, "wb") as f:
                os.chmod(self.configCacheName, stat.S_IRUSR | stat.S_IWUSR)
                pickle.dump(gConfigurationData.mergedCFG, f)
        else:
            gConfigurationData.mergedCFG = pickle.load(open(self.configCacheName, "rb"))
