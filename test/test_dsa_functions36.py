"""Test code for dsa_funcitons36.py
   execute 'pytest' to run tests.
"""

import sys
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsa_functions36 as df

class TestDsaFunctions36(unittest.TestCase):
    """This class is applying unit tests to the functions found in
    dsa_functions36.py
    """

    def test_read_yaml(self):
        # Test reading yaml files. returns the contents of the yaml file.

        result1 = df.read_yaml('test_etcdConfig.yml')
        self.assertEqual(result1, {'endpoints': ['192.168.1.132:2379']})
