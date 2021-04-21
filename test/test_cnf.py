"""Test code for cnf.py
   execute 'pytest' to run tests.
"""

import sys
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsautils.cnf as cnf
from pkg_resources import Requirement, resource_filename
ETCDCONF = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")
CNFCONF = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/cnfConfig.yml")

# example data
T2_DATA = {'min_dm': 50.0,
           'min_dm_dsc': 'smallest dm in filtering',
           'max_ibox': 20,
           'max_ibox_dsc': 'largest ibox in filtering',
           'min_snr': 7.75,
           'min_snr_dsc': 'smallest snr in filtering',
           'max_ncl': 10,
           'max_ncl_dsc': 'largest number of clusters allowed in triggering'
           }

FRINGE_DATA = {'test': False,
               'test_dsc': 'Indicates testing',
               'key_string': 'bada',
               'key_string_dsc': 'PSRDADA buffer name',
               'fringestop': True,
               'fringestop_dsc': 'bool to enable fringestopping',
               'samples_per_frame': 1,
               'samples_per_frame_dsc': '',
               'samples_per_frame_out': 1,
               'samples_per_frame_out_dsc': '',
               'nint': 24,
               'nint_dsc': 'Number of samples to integrate together',
               'nfreq_int': 1,
               'nfreq_int_dsc': 'Number of channels to integrate',
               'filelength_minutes' : 15,
               'nfreq_scrunch' : 48,
               'outrigger_delays': {
                                  100:  2400, # 3.6-1.2,
                                  101:  2400, # 3.6-1.2,
                                  102:   872, # Updated empirically. MC: 3.5-1.2,
                                  103:  1000, # 2.2-1.2,
                                  104:  3100, # 4.3-1.2,
                                  105: 11700, # 12.9-1.2,
                                  106:  9500, # 10.7-1.2,
                                  107: 10400, # 11.6-1.2,
                                  108: 11100, # 12.3-1.2,
                                  109: 12200, # 13.4-1.2,
                                  110: 16100, # 17.3-1.2,
                                  111: 15100, # 16.3-1.2,
                                  112: 15900, # 17.1-1.2,
                                  113: 17400, # 18.6-1.2,
                                  114: 19300, # 20.5-1.2,
                                  115: 21100, # 22.3-1.2,
                                  116:  4070, # Updated emprically. MC: 5.5-1.2,
                                  117:  5300, # 6.5-1.2
                              }
}
               
CORR_DATA = {'nant': 25,
             'nant_dsc': 'number of online antennas',
             'bw_GHz': 0.250,
             'bw_GHz_dsc': 'Bandwidth',
             'nchan': 8192,
             'nchan_dsc': 'Total number of channels before splitting into spws',
             'f0_GHz': 1.53,
             'f0_GHz_dsc': 'Frequency of the first channel before splitting into spws',
             'chan_ascending': False,
             'chan_ascending_dsc': 'bool to specify channel order',
             'npol': 2,
             'npol_dsc': 'Number of polarizations',
             'pt_dec': 0.9040805525,
             'pt_dec_dsc': 'Declination of the Crab',
             'tsamp': 0.134217728,
             'tsamp_dsc': 'Sampling time of data that will be read in',
             'antenna_order': {0: 24,
                               1: 25,
                               2: 26,
                               3: 27,
                               4: 28,
                               5: 29,
                               6: 30,
                               7: 31,
                               8: 32,
                               9: 33,
                               10: 34,
                               11: 35,
                               12: 20,
                               13: 19,
                               14: 18,
                               15: 17,
                               16: 16,
                               17: 15,
                               18: 14,
                               19: 13,
                               20: 100,
                               21: 101,
                               22: 102,
                               23: 116,
                               24: 103},
             'antenna_order_dsc': 'antenna mapping',
             'nchan_spw': 384,
             'nchan_spw_dsc': 'number of channels in a spectral window',
             'ch0': {'corr00': 1024,
                     'corr02': 1408,
                     'corr03': 1792,
                     'corr21': 2176,
                     'corr05': 2560,
                     'corr06': 2944,
                     'corr07': 3328,
                     'corr08': 3712,
                     'corr09': 4096,
                     'corr10': 4480,
                     'corr11': 4864,
                     'corr12': 5248,
                     'corr13': 5632,
                     'corr14': 6016,
                     'corr15': 6400,
                     'corr16': 6784},
             'pols_voltage': ['B', 'A'],
             'pols_corr': ['BB', 'AA']
}

CAL_DATA = {
        'caltime_minutes': 15,
        'refant': '102',
        'msdir': '/mnt/data/dsa110/calibration/',
        'beamformer_dir': '/home/user/beamformer_weights/',
        'hdf5_dir': '/mnt/data/dsa110/correlator/',
        'caltable': '/home/user/proj/dsa110-shell/dsa110-calib/dsacalib/data/calibrator_sources.csv',
        'weightfile': '/home/ubuntu/proj/dsa110-shell/dsa110-xengine/utils/antennas.out',
        'flagfile': '/home/ubuntu/proj/dsa110-shell/dsa110-xengine/scripts/flagants.dat',
        'bfarchivedir': '/mnt/data/dsa110/T3/calibs/'
    }

class TestCnf(unittest.TestCase):
    """This class is applying unit tests to the Conf class in
    cnf.py
    """
    def test_c_tor_exception(self):
        # Test contructor

        self.assertRaises(FileNotFoundError, cnf.Conf, 'abcd', 'efgh', False)

    def test_c_tor(self):
        my_cnf = cnf.Conf()
        self.assertIsInstance(my_cnf, cnf.Conf)

    def test_list(self):
        test_list = ['t2', 'corr', 'fringe', 'cal', 'snap', 'pipeline', 'search']
        my_cnf = cnf.Conf()
        my_list = my_cnf.list()
        self.assertEqual(my_list, test_list)

    def test_t2_no_etcd(self):
        my_cnf = cnf.Conf()
        t2_cnf = my_cnf.get('t2')
        self.assertEqual(t2_cnf.keys(), T2_DATA.keys())

    def test_fringe_no_etcd(self):
        my_cnf = cnf.Conf()
        fringe_cnf = my_cnf.get('fringe')
        self.assertEqual(fringe_cnf.keys(), FRINGE_DATA.keys())
        
    def test_corr_no_etcd(self):
        my_cnf = cnf.Conf()
        corr_cnf = my_cnf.get('corr')
        self.assertEqual(corr_cnf.keys(), CORR_DATA.keys())
        
    def test_cal_no_etcd(self):
        my_cnf = cnf.Conf()
        cal_cnf = my_cnf.get('cal')
        self.assertEqual(cal_cnf.keys(), CAL_DATA.keys())
        
    def test_etcd(self):
        pass
        #my_etcd = ds.DsaStore(etcdconf)
        #rtn_etcd = my_etcd.get_etcd()
        #self.assertIsInstance(rtn_etcd, Etcd3Client )
