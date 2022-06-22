""" COMDIRAC
"""
# Define Version
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
    version = __version__
except DistributionNotFound:
    # package is not installed
    version = "Unknown"


def extension_metadata():
    return {"priority": 11}
