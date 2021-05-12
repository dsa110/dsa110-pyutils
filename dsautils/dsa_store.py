"""Class for access to ETCD service. Coded against etcd3 v0.10.0 from pip.

   :example:

    >>> import dsautils.dsa_store as ds
    >>> my_ds = ds.DsaStore()
    >>> # put and get
    >>> my_ds.put_dict('/test/1',  {"a": 5.4})
    >>> v = my_ds.get_dict('/test/1')
    >>> print("v: ", v)
    >>>
    >>> # Get monitor data for antenna 24
    >>> 
    >>> vv = my_ds.get_dict('/mon/ant/24')
    >>> print("vv: ", vv)
    >>> print("vv['time']: ", vv['time'])
    >>>
    >>> # register a call back function on key: '/mon/ant/24'
    >>>
    >>> def my_cb(event: "Dictionary"):
    >>>     print(event)
    >>> # watch_id can be used to cancel watch with cancel() command.
    >>> watch_id = my_ds.add_watch('/mon/ant/24', my_cb)
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

etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")


class DsaStore:
    """ Accessor to the ETCD service. Production code should use
    the default constructor.

    raise: etcd3.exceptions.ConnectionFailedError, FileNotFoundError
    """

    def __init__(self, endpoint_config: "String" = etcdconf):
        """C-tor

        :param endpoint_config: Specify config file for Etcd endpoint. (Optional)
        :type endpoint_config: String
        """

        self.log = dsl.DsaSyslogger("dsa", "System", logging.INFO, "dsaStore")
        self.watch_ids = []
        try:
            etcd_config = df.read_yaml(endpoint_config)
            etcd_host, etcd_port = self._parse_endpoint(
                etcd_config['endpoints'])

            self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
            self.log.function('c-tor')
            self.log.info('DsaStore created')
        except:
            self.log.function('c-tor')
            self.log.error('Cannot create DsaStore')
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

    def put_dict(self, key: "string", value: "Dictionary"):
        """Put a dictionary into Etcd under the specified key.

        :param key: Key name to place data under. (Ex. '/mon/snap/1')
        :param value: Data to place into Etcd store.
        :type key: String
        :type value: Dictionary
        """

        self.log.function('put_dict')
        try:
            value_json = json.dumps(value)
            self.etcd.put(key, value_json)
        except ValueError:
            self.log.error('Could not serialize to json')
            raise

    def get_dict(self, key: "String") -> "Dictionary":
        """Get data from Etcd store in the form of a dictionary for the
        specified key.

        :param key: Etcd key from which to read data.
        :type key: String (Ex. '/mont/snap/1')
        """

        self.log.function('get_dict')
        # etcd returns a 2-tuple. We want the first element
        data = self.etcd.get(key)[0]
        if data is not None:
            try:
                return json.loads(data.decode("utf-8"))
            except:
                self.log.error('could not convert json to dictionary')
                raise
        else:
            self.log.warning('Nothing returned for key: {}'.format(key))

    def add_watch_prefix(self, key: str, cb_func: "function") -> int:
        """Add a callback function for the specified key prefix. This will
           call the callback for any key starting with the specified key prefix.

        The callback function must take a tuple as its argument. The
        tuple has the form: (key, dict) where key is the etcd key causing the
        callback to be called and 'dict' is the payload for that key.

        :param key: Key prefix to watch. Callback function will be called when contents of any key starting with prefix changes.
        :param cb_func: Callback function. Must take list as argument.
        :type key: str
        :type cb_func: function
        :rtype: int The watch id for the callback. Can be used to cancel watch.

        """

        watch_id = self.etcd.add_watch_prefix_callback(key, self._process_cb_prefix(cb_func))
        self.watch_ids.append(watch_id)
        return watch_id
        
    def add_watch(self, key: "String", cb_func: "Callback Function") -> int:
        """Add a callback function for the specified key.

        The callback function must take a dictionary as its argument. The
        dictionary will represent the payload associated with the key.

        :param key: Key to watch. Callback function will be called when contents of key changes.
        :param cb_func: Callback function. Must take dictionary as argument.
        :type key: String
        :type cb_func: Function(dictionary)
        :rtype: int

        """

        watch_id = self.etcd.add_watch_callback(key, self._process_cb(cb_func))
        self.watch_ids.append(watch_id)
        return watch_id

    def cancel(self, watch_id: int):
        """Cancel a callback for the specified watch_id.

        :param watch_id: The id of the watch callback.
        :type watch_id: int

        """
        self.etcd.cancel_watch(watch_id)

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
                if event is not None:
                    for ev in event.events:
                        key = ev.key.decode('utf-8')
                        value = ev.value.decode('utf-8')
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
                else:
                    self.log.warning('event is None.')
            except AttributeError:
                self.log.error('Unknown attribute in event.')
                raise
        return a

    def _process_cb_prefix(self, cb_func: "Callback Function"):
        """Private closure to call callback function with list argument
        representing the kay and payload of the keys being watched.

        :param cb_func: Callback function. Takes a list argument.
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
                if event is not None:
                    for ev in event.events:
                        key = ev.key.decode('utf-8')
                        value = ev.value.decode('utf-8')
                        # parse the JSON command into a dict.
                        try:
                            payload = self._parse_value(value)
                            cb_func((key, payload))
                        except ValueError:
                            self.log.error('problem parsing payload')
                            raise
                        except AttributeError:
                            self.log.error('Unknown attribute')
                            raise
                else:
                    self.log.warning('event is None')
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
