"""Test code for dsa_funcitons36.py
   execute 'pytest' to run tests.
"""

import sys
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsautils.dsa_functions36 as df
from pkg_resources import Requirement, resource_filename
import numpy as np
etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/test/etcdConfig.yml")

class TestDsaFunctions36(unittest.TestCase):
    """This class is applying unit tests to the functions found in
    dsa_functions36.py
    """

    def test_read_yaml(self):
        # Test reading yaml files. returns the contents of the yaml file.

        result1 = df.read_yaml(etcdconf)
        self.assertEqual(result1['endpoints'][0], '192.168.1.132:2379')

    def test_current_mjd(self):
        result = df.current_mjd()
        assert type(result) == np.float64
        assert result > 50000.
