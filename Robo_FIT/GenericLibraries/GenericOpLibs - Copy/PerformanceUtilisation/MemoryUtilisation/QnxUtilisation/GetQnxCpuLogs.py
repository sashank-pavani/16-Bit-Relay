""" All Lib file import which is required for this file"""
import threading
from time import sleep

from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLoggerHandler import SerialLoggerHandler


class GetQnxMemoryLogs:
    """ This class is used for taking QNX CPU Memory Logs into the file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.serial_logs = SerialLoggerHandler()
        self.thread_obj = None
        self.config_manager = ConfigurationManager()
        self.time_interval = self.config_manager.get_qnx_top_time_interval()
        self.cmd = self.config_manager.get_qnx_top_command()

    def capture_qnx_cpu_logs(self, test_case_name):
        """
        This Method is used to capture qnx cpu top log.
        :param test_case_name : name for save log qnx cpu.
        """
        try:
            self.thread_obj: threading.Timer = threading.Timer(self.time_interval,
                                                               self.capture_qnx_cpu_logs,
                                                               args=[test_case_name])
            self.thread_obj.start()
            self.serial_logs.write_command_on_serial(device='qnx', cmd='date -u "+Date: %d-%m-%Y Time: %H:%M:%S"', stop_prev=False)
            sleep(0.5)
            self.serial_logs.write_command_on_serial(device="qnx", cmd=self.cmd, stop_prev=False)
            sleep(5)
        except Exception as exp:
            robot_print_error(f"Error to capture the QNX logs, EXCEPTION: {exp}")

    def stop_qnx_mem_logs(self):
        """
        This method is used to stop the android memory thread.
        This thread is created by `get_android_mem_data(test_case_name: str)`
        :return: None
        """
        try:
            if self.thread_obj is not None and type(self.thread_obj) is threading.Timer:
                self.thread_obj.cancel()
            else:
                raise Exception("Its seems android memory thread object either "
                                "not created or already destroyed")
        except Exception as exp:
            robot_print_error("Can't stop the android memory thread.\nEXCEPTION: %s" % exp)
