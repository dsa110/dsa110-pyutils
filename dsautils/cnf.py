"""Class to provide configuration parameters used across codebase.
   Coded against etcd3 v0.10.0 from pip.

   :example:

    >>> import dsautils.cnf as cnf
    >>> my_cnf = cnf.Conf()
    >>> # get list of Subsystems available.
    >>> ss = my_cnf.list()
    >>> 
    >>> # get T2 configuration parameters
    >>> t2_cnf = my_cnf.get('t2')
    >>> print("t2_cnf: ", t2_cnf)
    >>>
    >>> # register a call back function on subsystem name: 't2'
    >>>
    >>> def my_cb(event: "Dictionary"):
    >>>     print(event)
    >>> my_ds.add_watch('t2', my_cb)
    >>> while True
    >>>    time.sleep(1)
"""

from typing import List
import logging
import etcd3
import json
import dsautils.dsa_functions36 as df
import dsautils.dsa_syslog as dsl
from pkg_resources import Requirement, resource_filename

ETCDCONF = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")
CNFCONF = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/cnfConfig.yml")

#ETCDMAP = {'t2': '/cnf/t2', 'corr': '/cnf/corr'}

T2_DATA = {'min_dm': 50.0,
           'min_dm_dsc': 'smallest dm in filtering',
           'max_ibox': 33,
           'max_ibox_dsc': 'largest ibox in filtering',
           'min_snr': 9.0,
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
               'nfreq_int': 8,
               'nfreq_int_dsc': 'Number of channels to integrate',
               'filelength_minutes' : 5,
               'nfreq_scrunch' : 48,
               'outrigger_delays' : {
                   100:  1774, # 3.6-1.2,
                   101:  2400-764, # 798, # 3.6-1.2,
                   102:  2300-708, #-2506, # Updated empirically. MC: 3.5-1.2,
                   103:  1000-1318, #3778, # Updated empirically. MC: 2.2-1.2,
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
                   116:  3712, # Updated emprically. MC: 5.5-1.2,
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
             'pt_dec': 0.4569271982,
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
             'ch0': {'corr01': 1024,
                     'corr02': 1408,
                     'corr03': 1792,
                     'corr04': 2176,
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
    'refant': ['116', '101'],
    'msdir': '/mnt/data/dsa110/calibration/',
    'beamformer_dir': '/home/user/beamformer_weights/',
    'hdf5_dir': '/mnt/data/dsa110/correlator/',
    'caltable': '/home/user/proj/dsa110-shell/dsa110-calib/dsacalib/data/calibrator_sources.csv',
    'weightfile': '/home/ubuntu/proj/dsa110-shell/dsa110-xengine/utils/antennas.out',
    'flagfile': '/home/ubuntu/proj/dsa110-shell/dsa110-xengine/scripts/flagants.dat',
    'bfarchivedir': '/mnt/data/dsa110/T3/calibs/'
}
    
MINMAX_ANT_DATA = {'mp_age_seconds': [0, 5],
                   'sim': [False, True],  # initialized directly
                   'ant_el': [0., 145.],
                   'ant_cmd_el': [0., 145.],
                   'drv_cmd': [0, 2],
                   'drv_act': [0, 2],
                   'drv_state': [1, 2],
                   'at_north_lim': [False, True],
                   'at_south_lim': [False, True],
                   'brake_on': [False, True],
                   'emergency_off': [False, True],
                   'motor_temp': [-10., 40.],
                   #          'focus_temp': [],
                   'lna_current_a': [45., 85.],
                   'lna_current_b': [45., 85.],
                   'noise_a_on': [False, True],
                   'noise_b_on': [False, True],
                   'rf_pwr_a': [-80., -60.],
                   'rf_pwr_b': [-80., -60.],
                   'feb_current_a': [240., 300.],
                   'feb_current_b': [240., 300.],
                   'laser_volts_a': [2.5, 3.1],
                   'laser_volts_b': [2.5, 3.1],
                   'feb_temp_a': [-10., 60.],
                   'feb_temp_b': [-10., 60.],
                   #          'psu_volt': [],
                   #          'lj_temp': [],
                   'fan_err': [False, True],
                   #          'emergency_off': [False, True]  # what is good/bad here?
}

MINMAX_BEB_DATA = {'mp_age_seconds': [0, 5],
                   'pd_current_a': [0.6, 3.0],
                   'pd_current_b': [0.6, 3.0],
                   'if_pwr_a': [-55, -38],
                   'if_pwr_b': [-55, -38],
                   'lo_mon': [2.4, 3],
                   'beb_current_a': [270, 375],
                   'beb_current_b': [210, 325],
                   'beb_temp': [20, 45]
}

MINMAX_SERVICE_DATA = {'mp_age_seconds': [0, 60]}   # TODO: set based on service update cadence

DATA = {'t2': T2_DATA,
        'fringe': FRINGE_DATA,
        'corr': CORR_DATA,
        'cal': CAL_DATA,
        'minmax_ant': MINMAX_ANT_DATA,
        'minmax_beb': MINMAX_BEB_DATA,        
        'minmax_service': MINMAX_SERVICE_DATA
}

class Conf:
    """ Accessor for configuration parameters

    raise: etcd3.exceptions.ConnectionFailedError, FileNotFoundError
    """

    def __init__(self, endpoint_conf: "String" = ETCDCONF, cnf_conf: "String" = CNFCONF, use_etcd: "bool" = False,
                 data: "dict"= DATA):
        """C-tor

        :param endpoint_conf: Specify config file for Etcd endpoint.(Optional)
        :param cnf_conf: Specify config file for subsystem mapping.(Optional)
        :param use_etcd: Set to True to load config from etcd.
        :type endpoint_conf: String
        :type cnf_conf: String
        :type use_etcd: Bool
        """

        self.log = dsl.DsaSyslogger("dsa", "System", logging.INFO, "Conf")
        self.use_etcd = use_etcd
        self.data = data
        self.watch_ids = []
        try:
            etcd_config = df.read_yaml(endpoint_conf)
            etcd_host, etcd_port = self._parse_endpoint(
                etcd_config['endpoints'])

            self.etcd = etcd3.client(host=etcd_host, port=etcd_port)

            try:
                self.cnf_config = df.read_yaml(cnf_conf)
            except:
                self.log.function('c-tor')
                self.log.error("Cannot read cnf_conf YAML file")
                raise
            self.log.function('c-tor')
            self.log.info('Conf created')
        except:
            self.log.function('c-tor')
            self.log.error('Cannot create Conf')
            raise

    def _parse_endpoint(self, endpoint: "List") -> "Tuple":
        """Parse the endpoint string in the first element of the list.
           Go allows multiple endpoints to be specified
           whereas Python only one and has separate args for host and port.

        :param endpoint: host port string of the form host:port.
        :type endpoint: List
        :return: Tuple (host, port)
        :rtype: Tuple
        :raise: ValueError
        """

        host, port = endpoint[0].split(':')
        self.log.function('_parse_endpoint')
        try:
            self._check_host(host)
        except:
            self.log.critical('Could not parse endpoint')
            raise
        try:
            self._check_port(port)
        except:
            self.log.critical('Could not parse port')
            raise

        return host, port

    def _check_host(self, host_name: "String"):
        self.log.function('_check_host')
        self.log.info('TODO: implement')
        pass

    def _check_port(self, port: "String"):
        self.log.function('_check_port')
        self.log.info('TODO: implement')
        pass

    def get_etcd(self) -> "Etcd3Client Object":
        """ Return the etcd object
        """
        return self.etcd

    def list(self) -> "list":
        """list returns a list of subsystem names
        """
        return list(self.cnf_config.keys())
    
    def get(self, ss_name: "String") -> "Dictionary":
        """Get configuration data for a specified subsystem name.

        :param ss_name: Logical name for subsystem.
        :type ss_name: String (Ex. 't2', 'ant', 'corr)
        """

        self.log.function('get')
        key = self.cnf_config[ss_name]

        if self.use_etcd:
            # etcd returns a 2-tuple. We want the first element
            data = self.etcd.get(key)[0]
            try:
                return json.loads(data.decode("utf-8"))
            except:
                self.log.error('could not convert json to dictionary')
                raise
        else:
            try:
                return self.data[ss_name]
            except:
                self.log.error('Unknown Subsystem name: {}'.format(ss_name))

    def add_watch(self, ss_name: "String", cb_func: "Callback Function"):
        """Add a callback function for the specified subsystem name.

        The callback function must take a dictionary as its argument. The
        dictionary will represent the payload associated with the name.

        :param ss_name: Subsystem to watch. Callback function will be called when contents of subsystem changes.
        :param cb_func: Callback function. Must take dictionary as argument.
        :type ss_name: String (i.e. 't2', 'ant', 'corr')
        :type cb_func: Function(dictionary)
        """

        key = self.cnf_config[ss_name]
        watch_id = self.etcd.add_watch_callback(key, self._process_cb(cb_func))
        self.watch_ids.append(watch_id)

    def get_watch_ids(self) -> "List":
        """Return the array of watch_ids
        """
        return self.watch_ids

    def _process_cb(self, cb_func: "Callback Function"):
        """Private closure to call callback function with dictionary argument
        representing the payload of the key being watched.

        :param cb_func: Callback function. Takes a dictionary argument.
        :type cb_func: Function
        """

        self.log.function('_process_cb')

        def a(event):
            """Function Etcd actually calls. We process the event so the caller
            doesn't have to.

            :param event: A WatchResponse object
            :raise: ValueError
            :raise: AttributeError
            """
            try:
                key = event.events[0].key.decode('utf-8')
                value = event.events[0].value.decode('utf-8')
                # parse the JSON command into a dict.
                try:
                    payload = self._parse_value(value)
                    cb_func(payload)
                except ValueError:
                    self.log.error('problem parsing payload')
                    raise
                except AttributeError:
                    self.log.error('Unknown attribute')
                    raise
            except AttributeError:
                self.log.error('Unknown attribute in event.')
                raise
        return a

    def _parse_value(self, value: "Json String") -> "Dictionary":
        """Parse the string in JSON format into a dictionary.

        :param value: JSON string of the form: {"key":"value"}
                      or {"key":number|bool}
        :type value: String
        :return: Key,value dictionary
        :rtype: Dictionary
        :raise: ValueError
        """

        self.log.function('_parse_value')
        rtn = {}
        try:
            rtn = json.loads(value)
        except ValueError:
            # TODO: log to syslog
            self.log.error("JSON Decode Error. value= {}".format(value))
            raise
        return rtn
