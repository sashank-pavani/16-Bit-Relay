"""Importing all needed lib"""
import threading
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLoggerHandler import SerialLoggerHandler


class GetQnxCpuLogs:
    """ This class is used for taking CPU QNX Memory Logs into the file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.serial_logs = SerialLoggerHandler()
        self.top_thread_obj = None
        self.config_manager = ConfigurationManager()
        self.time_interval = self.config_manager.get_qnx_top_time_interval()
        self.top_command = self.config_manager.get_qnx_top_command()

    def __capture_qnx_logs(self, command: str):
        """
        This method is used to capture the logs from QNX port using given command
        :param command: Command need to be execute on the QNX port
        :type command: String
        :return: None
        :rtype: None
        """
        try:
            self.serial_logs.write_command_on_serial(device='qnx', cmd='date -u "+Date: %d-%m-%Y Time: %H:%M:%S"', stop_prev=False)
            sleep(5)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=command)
            sleep(5)
        except Exception as exp:
            robot_print_error(
                f"Error to capture the qnx logs for command: {command}, EXCEPTION: {exp}")

    def capture_qnx_top_logs(self):
        """
        This method is used to execute the QNX top command.
        its execute `top -i 1 -z 40`
        :return: None
        :rtype: None
        """
        try:
            self.top_thread_obj: threading.Timer = threading.Timer(self.time_interval,
                                                                   self.capture_qnx_top_logs)
            self.top_thread_obj.start()
            self.serial_logs.write_command_on_serial(device='qnx', cmd='date -u "+Date: %d-%m-%Y Time: %H:%M:%S"', stop_prev=False)
            sleep(0.5)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=self.top_command, stop_prev=False)
            sleep(6)
        except Exception as exp:
            robot_print_error(f"Error to capture the QNX logs, EXCEPTION: {exp}")

    def stop_qnx_cpu_logs(self, log_type: str):
        """
        This method is used to stop the QNX cpu logs base on the log_type provided by the user.
        :param log_type: Type of the logs as below:
            1. for top: "top"
        User doesn't need to take care of these argument as these are externally handle by the framework.
        :return: None
        """
        try:
            obj = None
            if log_type == "top":
                obj = self.top_thread_obj
            else:
                robot_print_error(f"Invalid log type pass to the stop method")
            if obj is not None and isinstance(obj, threading.Timer):
                obj.cancel()
            else:
                raise Exception("Its seems android memory thread object either "
                                "not created or already destroyed")
        except Exception as exp:
            robot_print_error("Can't stop the android memory thread.\nEXCEPTION: %s" % exp)
