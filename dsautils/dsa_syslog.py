"""Class to provide logging to syslog on Linux using structured logging.

   Current MJD will be added to log message at time of logging. See example
   output below.

   :example:

    >>> import dsautils.dsa_syslog as dsl
    >>> my_log = dsl.DsaSyslogger()
    >>> my_log.subsystem('correlator')
    >>> my_log.app('run_corr')
    >>> my_log.version('v1.0.0')
    >>> my_log.function('setup')
    >>> my_log.info('corr01 configured')
    >>>
    >>> # Look into /var/log/syslog
    >>> Jul 10 15:40:31 birch 2020-07-10T22:40:31 [info     ] {"mjd": 59040.944796612166, "subsystem": "correlator", "app": "run_corr, "version": "v1.0.0", "module": "dsautils.dsa_syslog", "function": "setup", "msg": "corr01 configured"}
"""

import logging
import logging.handlers
import structlog
#logging.basicConfig()
from structlog.stdlib import LoggerFactory
from collections import OrderedDict
import json
from astropy.time import Time

class DsaSyslogger:
    """Class for writing semantic logs to syslog
    """

    def __init__(self):
        
        timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S")
        shared_processors = [
            structlog.stdlib.add_log_level,
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

        handler = logging.handlers.SysLogHandler(address = '/dev/log')
        handler.setFormatter(formatter)

        self.log = logging.getLogger(__name__)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

        self.msg = OrderedDict({'mjd': 0.0,
                    'subsystem': '-',
                    'app': '-',
                    'version': '-',
                    'module': __name__,
                    'function': '-'})
                    
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

        BUG: Setting logging.DEBUG does not show debug logs.

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

        self.msg['mjd'] = Time.now().mjd
        self.msg['msg'] = event
        msgs = json.dumps(self.msg)
        log_func(msgs)
        
    def debug(self, event: "String"):
        """Support log.debug

        BUG: Debug levels not showing up in syslog
        """
        self._logit(event, self.log.debug)
        
    def info(self, event: "String"):
        """Support log.info
        """
        self._logit(event, self.log.info)

    def warning(self, event: "String"):
        """Support log.warning
        """
        self._logit(event, self.log.warning)

    def error(self, event: "String"):
        """Support log.errror
        """
        self._logit(event, self.log.error)
        
    def critical(self, event: "String"):
        """Support log.critical
        """
        self._logit(event, self.log.critical)
