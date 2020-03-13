""" Common functions for all to use.
    All functions must be documented and have an associated unit test.
    Coded against yaml 5.3 (pip install PyYAML)
"""

import yaml


def read_yaml(fname: "string") -> "Dictionary":
    """Read a YAML formatted file.

    :param fn: YAML formatted filename"
    :type fn: String
    :return: Dictionary on success. None on error
    :rtype: Dictionary
    """

    with open(fname, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            return None
