''' Ant is a class to encapsulate controlling a DSA110 Antenna.

    >>> # Example using Ant class
    >>>
    >>> import dsautils.dsa_ant as ant
    >>> ant99 = ant.Ant(99)
    >>> ant99.move(33.2)
    >>> ant99.noise_a_on(True)
    >>> ant99.noise_b_on(True)
    >>> ant99.noise_ab_on(False)
'''

import sys
from pathlib import Path
from pkg_resources import Requirement, resource_filename
import dsautils.dsa_store as ds
ETCDCONF = resource_filename(Requirement.parse("dsa110-pyutils"),
                             "dsautils/conf/etcdConfig.yml")
sys.path.append(str(Path('..')))

CMD_KEY_BASE = '/cmd/ant/'
MON_KEY_BASE = '/mon/ant/'


class Ant():
    """Class encapsulates controlling DSA110 antenna.
    """
    def __init__(self, ant_num):
        '''c-tor. Specify anntenna number. Use 0 for all antennas

        :param ant_num: Antenna number or list of antennas to control. 0 for all.
        :type ant_name: Integer or Array of Integers.
        '''
        self.ant_nums = []
        # Test contructor
        if isinstance(ant_num, list):
            self.ant_nums = ant_num
        else:
            self.ant_nums.append(ant_num)

        self.my_store = ds.DsaStore(ETCDCONF)
        self.cmd_key_base = CMD_KEY_BASE
        self.mon_key_base = MON_KEY_BASE

    def _send(self, cmd):
        '''Private helper to send command dictionary to antenna.

        :param cmd: Dictionary containing antenna command.
        :type cmd: Dictionary
        '''
        for ant in self.ant_nums:
            self.my_store.put_dict(self.cmd_key_base + str(ant), cmd)

    def move(self, el_in_deg):
        '''Move antenna elevation.

        :param el_in_deg: Elevation angle in degrees.
        :type el_in_deg: Float
        '''

        cmd = {}
        cmd['cmd'] = 'move'
        cmd['val'] = el_in_deg
        self._send(cmd)

    def noise_a_on(self, onoff):
        '''Turn noise A dioode on or off.

        :param onoff: True for On. Falase for Off.
        :type onoff: Boolean
        '''

        cmd = {}
        cmd['cmd'] = 'noise_a_on'
        cmd['val'] = onoff
        self._send(cmd)

    def noise_b_on(self, onoff):
        '''Turn noise B dioode on or off.

        :param onoff: True for On. Falase for Off.
        :type onoff: Boolean
        '''
        cmd = {}
        cmd['cmd'] = 'noise_b_on'
        cmd['val'] = onoff
        self._send(cmd)

    def noise_ab_on(self, onoff):
        '''Turn noise A,B dioode on or off.

        :param onoff: True for On. Falase for Off.
        :type onoff: Boolean
        '''
        self.noise_a_on(onoff)
        self.noise_b_on(onoff)

    def add_watch(self, cb_func: "Callback Function", ant_num=0):
        """Add a callback function for the specified key.

        The callback function must take a dictionary as its argument. The
        dictionary will represent payloads associated with an antenna.
        The call back must be made thread safe if passing in a list of
        antennas as it will likely be called at the same time for
        different antennas. Default antenna number is 0 for all.

        :param cd_func: Callback function. Must take dictionary as argument.
        :param ant_num: Antenna number. 0 for all. Or a list of antenna numbers.
        :type cd_func: Function(dictionary)
        :type ant_nums: Integer or Array of integers
        """
        ant_cb_nums = []
        if isinstance(ant_num, list):
            ant_cb_nums = ant_num
        else:
            ant_cb_nums.append(ant_num)

        for ant in ant_cb_nums:
            self.my_store.add_watch(self.mon_key_base + str(ant), cb_func)
