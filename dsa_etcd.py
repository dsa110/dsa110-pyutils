"""Class for access to ETCD service. Coded against etcd3 v0.10.0 from pip.

   :example:

    >>> import dsa_etcd as de
    >>> my_de = de.DsaEtcd()
    >>> # put and get
    >>> my_de.put_dict('/test/1',  '{"a": 5.4}')
    >>> v = my_de.get_dict('/test/1')
    >>> print("v: ", v)
    >>>
    >>> # Get monitor data for antenna 24
    >>> 
    >>> vv = my_de.get_dict('/mon/ant/24')
    >>> print("vv: ", vv)
    >>> print("vv['time']: ", vv['time'])
"""

import etcd3
import json
import dsa_functions36 as df


class DsaEtcd:
    """ Accessor to the ETCD service. Production code should use
        the default constructor.
    """
    def __init__(self, endpoint_config: "String" = "etcdConfig.yml"):
        try:
            etcd_config = df.read_yaml(endpoint_config)
            etcd_host, etcd_port = self._parse_endpoint(
                etcd_config['endpoints'])

            self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
        except:
            raise

    def _parse_endpoint(self, endpoint: "List") -> "Tuple":
        """Parse the endpoint string in the first element of the list.
           Go allows multiple endpoints to be specified
           whereas Python only one and has separate args for host and port.

        :param endpoint: host port string of the form host:port.
        :type endpoint: List
        :return: Tuple (host, port)
        :rtype: Tuple
        """

        host, port = endpoint[0].split(':')
        return host, port

    def get_etcd(self) -> "Etcd3Client Object":
        """ Return the etcd object
        """
        return self.etcd

    def put_dict(self, key: "string", value: "Dictionary"):
        """Put a dictionary into Etcd under the specified key.

        :param key: Key name to place data under. (Ex. '/mon/snap/1')
        :param value: Data to place into Etcd store.
        :type key: String
        :type value: Dictionary
        """
        try:
            value_json = json.dumps(value)
            self.etcd.put(key, value_json)
        except ValueError:
            raise

    def get_dict(self, key: "String") -> "Dictionary":
        """Get data from Etcd store in the form of a dictionary for the
        specified key.

        :param key: Etcd key from which to read data.
        :type key: String (Ex. '/mont/snap/1')
        """

        # etcd returns a 2-tuple. We want the first element
        data = self.etcd.get(key)[0]
        try:
            return json.loads(data.decode("utf-8"))
        except:
            raise
