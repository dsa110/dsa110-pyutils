"""Test code for dsa_store.py
   execute 'pytest' to run tests.
"""

import sys
import math
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsautils.dsa_store as ds
from pkg_resources import Requirement, resource_filename
etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")

class TestDsaStore(unittest.TestCase):
    """This class is applying unit tests to the DsaStore class in
    dsa_etcd.py
    """
    def test_c_tor_exception(self):
        # Test contructor

        self.assertRaises(FileNotFoundError, ds.DsaStore, 'abcd')

    def test_c_tor(self):
        my_etcd = ds.DsaStore(etcdconf)
        self.assertIsInstance(my_etcd, ds.DsaStore)

    def test_put_get(self):
        my_etcd = ds.DsaStore(etcdconf)
        test_dict = {}
        test_dict['value'] = 23.4
        test_dict['value2'] = 23
        test_dict['value3'] = 'value3'
        my_etcd.put_dict('/test/1', test_dict)
        rtn_dict = my_etcd.get_dict('/test/1')
        self.assertEqual(rtn_dict, test_dict)

    def put_bad_val(self, val):
        my_etcd = ds.DsaStore(etcdconf)
        test_bad_val = {}
        test_bad_val['value'] = val
        a = 0
        try:
            my_etcd.put_dict('/test/1', test_bad_val)
            my_etcd.put_dict('/test/1', test_bad_val, True)
            a = 1
        except ValueError as ve:
            self.assertIsInstance(ve, ValueError)
        except Exception as other:
            self.assertIsInstance(other, ds.DsaStore)
        self.assertEqual(a, 0)

    def test_put_NaN(self):
        self.put_bad_val(math.nan)

    def test_put_Inf(self):
        self.put_bad_val(math.inf)

    def test_put_minus_Inf(self):
        self.put_bad_val(-math.inf)
        
    def test_put_NaN_allow(self):
        my_etcd = ds.DsaStore(etcdconf)
        test_dict = {}
        test_dict['value'] = math.nan
        test_dict['value2'] = 23
        test_dict['value3'] = 'value3'
        a = 0
        try:
            my_etcd.put_dict('/test/1', test_dict, False)
            a = 1
        except ValueError as ve:
            self.assertIsInstance(ve, ValueError)
        except Exception as other:
            self.assertIsInstance(other, ds.DsaStore)
        self.assertEqual(a, 1)

    def _get_val(self, val):
        """Helper to check whether valueError is thrown when val = NaN, -Infinity, Infinity
        """
        my_etcd = ds.DsaStore(etcdconf)
        test_dict = {}
        test_dict['value'] = val
        my_etcd.put_dict('/test/1', test_dict, False)
        a = 0
        try:
            rtn_dict = my_etcd.get_dict('/test/1')
            a = 1
        except ValueError as ve:
            self.assertIsInstance(ve, ValueError)
        except Exception as other:
            self.assertIsInstance(other, ds.DsaStore)
        self.assertEqual(a, 0)

    def test_get_Nan(self):
        self._get_val(math.nan)

    def test_get_minus_Infinity(self):
        self._get_val(-math.inf)

    def test_get_Ininity(self):
        self._get_val(math.inf)
        
    def _get_val_allow(self, val):
        """Helper to check whether val = NaN, -Infinity, Infinity is allowed. ie. no exceptions thrown.
        """
        my_etcd = ds.DsaStore(etcdconf)
        test_dict = {}
        test_dict['value'] = val
        my_etcd.put_dict('/test/1', test_dict, False)
        a = 0
        try:
            rtn_dict = my_etcd.get_dict('/test/1', None)
            a = 1
        except ValueError as ve:
            self.assertIsInstance(ve, ValueError)
        except Exception as other:
            self.assertIsInstance(other, ds.DsaStore)
        self.assertEqual(a, 1)

    def test_get_Nan_allow(self):
        self._get_val_allow(math.nan)

    def test_get_minus_Infinity_allow(self):
        self._get_val_allow(-math.inf)

    def test_get_Ininity_allow(self):
        self._get_val_allow(math.inf)

    def test_etcd(self):
        my_etcd = ds.DsaStore(etcdconf)
        rtn_etcd = my_etcd.get_etcd()
        #self.assertIsInstance(rtn_etcd, Etcd3Client )
