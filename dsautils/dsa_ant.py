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
sys.path.append(str(Path('..')))
import dsautils.dsa_store as ds
from pkg_resources import Requirement, resource_filename
etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")

class Ant():
    """Class encapsulates controlling DSA110 antenna.
    """
    def __init__(self, ant_num):
        '''c-tor. Specify anntenna number. Use 0 for all antennas

        :param ant_num: Antenna number to control. 0 for all.
        :type ant_name: Integer
        '''
        
        # Test contructor

        self.ant_num = ant_num
        self.my_etcd = ds.DsaStore(etcdconf)
        self.key = '/cmd/ant/' + str(ant_num)

    def _send(self, cmd):
        '''Private helper to send command dictionary to antenna.

        :param cmd: Dictionary containing antenna command.
        :type cmd: Dictionary
        '''
        
        self.my_etcd.put_dict(self.key, cmd)
        
    def move(self, elInDeg):
        '''Move antenna elevation.

        :param elInDeg: Elevation angle in degrees.
        :type elInDeg: Float
        '''
        
        cmd = {}
        cmd['cmd'] = 'move'
        cmd['val'] = elInDeg
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
