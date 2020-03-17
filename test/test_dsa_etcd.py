"""Test code for dsa_funcitons36.py
   execute 'pytest' to run tests.
"""

import sys
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsautils.dsa_etcd as de
from pkg_resources import Requirement, resource_filename
etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")

class TestDsaEtcd(unittest.TestCase):
    """This class is applying unit tests to the DsaEtcd class in
    dsa_etcd.py
    """
    def test_c_tor_exception(self):
        # Test contructor

        self.assertRaises(FileNotFoundError, de.DsaEtcd, 'abcd')

    def test_c_tor(self):
        my_etcd = de.DsaEtcd(etcdconf)
        self.assertIsInstance(my_etcd, de.DsaEtcd)

    def test_put_get(self):
        my_etcd = de.DsaEtcd(etcdconf)
        test_dict = {}
        test_dict['value'] = 23.4
        test_dict['value2'] = 23
        test_dict['value3'] = 'value3'
        my_etcd.put_dict('/test/1', test_dict)
        rtn_dict = my_etcd.get_dict('/test/1')
        self.assertEqual(rtn_dict, test_dict)

    def test_etcd(self):
        my_etcd = de.DsaEtcd(etcdconf)
        rtn_etcd = my_etcd.get_etcd()
        #self.assertIsInstance(rtn_etcd, Etcd3Client )
