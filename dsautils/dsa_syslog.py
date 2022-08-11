"""Class to provide logging to syslog on Linux using structured logging.

   This class is not thread safe.

   Current MJD will be added to log message at time of logging. See example
   output below.

   :example:

    >>> import logging
    >>> import dsautils.dsa_syslog as dsl
    >>> my_log = dsl.DsaSyslogger('dsa', 'correlator', logging.DEBUG, 'corr_logger')
    >>> my_log.app('run_corr')
    >>> my_log.version('v1.0.0')
    >>> my_log.function('setup')
    >>> my_log.info('corr01 configured')
    >>>
    >>> # Look into /var/log/syslog
    >>> Jul 10 15:40:31 birch 2020-07-10T22:40:31 [info     ] \
{"mjd": 59040.944796612166, "subsystem": "correlator", "app": "run_corr, \
"version": "v1.0.0", "module": "dsautils.dsa_syslog", "function": "setup", \
"msg": "corr01 configured"}
"""

import datetime
import socket
import logging
import logging.handlers
from collections import OrderedDict
import json
from multiprocessing import Lock
from structlog.stdlib import LoggerFactory
import structlog
from astropy.time import Time


class DsaSyslogger:
    """Class for writing semantic logs to syslog
    """
    def __init__(self,
                 proj_name='dsa',
                 subsystem_name='_',
                 log_level=logging.INFO,
                 logger_name=__name__,
                 log_stream=None):
        """C-tor

        :param proj_name: Project name
        :param subsystem_name: Subsystem or Category for this logger
        :param log_level: Logging Level(ie. Logging.INFO, Logging.DEBUG)
        :param loger_name: Name used to control scope of logger. \
Loggers with the same name are global within the Python interpreter instance.
        :param log_stream: Use Stream instead of syslog.
        :type proj_name: String
        :type subsystem_name: String
        :type log_level: logging.Level
        :type logger_name: String
        :type log_stream: Stream
        """

        
        host_name = socket.gethostname()
        timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S " + host_name + " ./py[]: ")
        shared_processors = [
            timestamper,
        ]

        structlog.configure(
            processors=shared_processors + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_pre_chain=shared_processors,
        )

        if log_stream is not None:
            handler = logging.StreamHandler(log_stream)
        else:
            try:
                handler = logging.handlers.SysLogHandler(address=('localhost', 514),
                                                         facility=logging.handlers.SysLogHandler.LOG_LOCAL0,
                                                         socktype=socket.SOCK_STREAM)
            except ConnectionRefusedError:
                try:
                    handler = logging.handlers.SysLogHandler(address=('localhost', 514),
                                                             facility=logging.handlers.SysLogHandler.LOG_LOCAL0,
                                                             socktype=socket.SOCK_DGRAM)
                except:
                    handler = logging.StreamHandler()
                    
        handler.setFormatter(formatter)

        self.log = logging.getLogger(logger_name)
        self.log.addHandler(handler)
        self.log.setLevel(log_level)

        self.msg = OrderedDict({
            'mjd': 0.0,
            'proj': proj_name,
            'subsystem': subsystem_name,
            'app': '_',
            'version': '_',
            'module': logger_name,
            'function': '_'
        })
        self.mutex = Lock()


    def subsystem(self, name: "String"):
        """Add subsystem name.

        :param name: Name of subsystem
        :type name: String
        """
        self.msg['subsystem'] = name

    def app(self, name: "String"):
        """Add application name.

        :param name: Name of application
        :type name: String
        """
        self.msg['app'] = name

    def version(self, name: "String"):
        """Add version.

        :param name: version of application/module
        :type name: String
        """
        self.msg['version'] = name

    def function(self, name: "String"):
        """Add function name

        :param name: function name
        :type name: String
        """
        self.msg['function'] = name

    def level(self, level: "logging.level"):
        """Set logging level

        :param level: Logging level(ie. logging.DEBUG, logging.INFO, etc)
        :type level: logging.Level
        """
        self.log.setLevel(level)

    def _logit(self, event: "String", log_func: "logging function"):
        """Log message to syslog

        :param event: message to log
        :param log_func: logging function to use
        :type event: String
        :type log_func: Function
        """

        try:
            d_utc = datetime.datetime.utcnow() # <-- get time in UTC
            self.msg['time'] = d_utc.isoformat("T") + "Z"
            self.msg['mjd'] = Time.now().mjd
            self.msg['msg'] = event
            msgs = json.dumps(self.msg)
            log_func(msgs)
        except BrokenPipeError as bpe:
            print("dsa_syslog:_logit. Exception: ", bpe)

    def debug(self, event: "String"):
        """Support log.debug

        On some systems, writing to debug ends up in /var/log/debug
        and not /var/log/syslog.
        """
        with self.mutex:
            self.msg['level'] = "debug"
            self._logit(event, self.log.debug)

    def info(self, event: "String"):
        """Support log.info
        """
        with self.mutex:
            self.msg['level'] = "info"
            self._logit(event, self.log.info)

    def warning(self, event: "String"):
        """Support log.warning
        """
        with self.mutex:
            self.msg['level'] = "warn"
            self._logit(event, self.log.warning)

    def error(self, event: "String"):
        """Support log.error
        """
        with self.mutex:
            self.msg['level'] = "error"
            self._logit(event, self.log.error)

    def critical(self, event: "String"):
        """Support log.critical
        """
        with self.mutex:
            self.msg['level'] = "critical"
            self._logit(event, self.log.critical)
