from logging.handlers import SysLogHandler as Syslog
import sys
from pathlib import Path
import unittest
sys.path.append(str(Path('..')))
import dsautils.dsa_syslog as dsl
from pkg_resources import Requirement, resource_filename
etcdconf = resource_filename(Requirement.parse("dsa110-pyutils"), "dsautils/conf/etcdConfig.yml")
import multiprocessing
from multiprocessing import Process

class TestDsaSyslogger(unittest.TestCase):
    """Class TestDsaSyslogger applies unit tests to dsa_syslogger
    """

    def test_c_tor(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_c_tor')
        loggr.info("C-tor test passed")

    def test_log_info(self):
        loggr1 = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr1, dsl.DsaSyslogger)
        loggr1.app("test_dsa_syslog")
        loggr1.version("v1.0.0")
        loggr1.function('test_log_info')
        loggr1.info("log info message in test_log_info()")

    def test_log_warning(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_log_warning')
        loggr.warning("log warning message")

    def test_log_debug(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_log_debug')
        loggr.debug("log debug message")

    def test_log_error(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_log_error')
        loggr.error("log error message")

    def test_log_critical(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_log_critical')
        loggr.critical("log critical message")

    def thread_func(self):
            logr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
            logr.info("inside thread_func")
            self.assertIsInstance(logr, dsl.DsaSyslogger)
            logr.app("test_dsa_syslog")
            logr.version("v1.0.0")
            logr.function('test_thread_safety')
            tid = multiprocessing.current_process().pid
            n_msgs = 1
            for idx in range(n_msgs):
                logr.info("thread id: {}".format(tid))
    
    def test_thread_safety(self):
        loggr = dsl.DsaSyslogger(subsystem_name="test",log_level=Syslog.LOG_INFO,logger_name="TestDsaSyslogger")
        self.assertIsInstance(loggr, dsl.DsaSyslogger)
        loggr.app("test_dsa_syslog")
        loggr.version("v1.0.0")
        loggr.function('test_thread_safety')

        
        n_threads = 2
        for idx in range(n_threads):
            loggr.info("Starting threads...{}".format(multiprocessing.current_process().pid))
            p = Process(target=self.thread_func)
            loggr.info("p {}...{}".format(p, multiprocessing.current_process().pid))            
            p.start()
            p.join()

