""" Common functions for all to use.
    All functions must be documented and have an associated unit test.
    Coded against yaml 5.3 (pip install PyYAML)
"""

import datetime
import yaml
from astropy.time import Time


def read_yaml(fname: "string") -> "Dictionary":
    """Read a YAML formatted file.

    :param fname: YAML formatted filename"
    :type fname: String
    :return: Dictionary on success. None on error
    :rtype: Dictionary
    """

    with open(fname, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            return None

def current_mjd() -> float:
    """Get the current time in mjd format.

    :return: Current time in MJD format.
    :rtype: float
    """
    return Time(datetime.datetime.utcnow()).mjd
