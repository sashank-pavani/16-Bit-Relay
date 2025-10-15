""" All Lib file import which is required for this file"""
import threading
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import \
    ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_error, robot_print_info, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLoggerHandler import \
    SerialLoggerHandler


class GetQnxMemoryLogs:
    """ This class is used for taking QNX Memory Logs into the file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.slog_thread = None
        self.serial_logs = SerialLoggerHandler()
        self.showmem_a_thread = None
        self.showmem_s_thread: threading.Timer = None
        self.ufs_thread = None
        self.config_manager = ConfigurationManager()
        robot_print_debug(f"Initializing of {__class__} complete")

    def __capture_qnx_logs(self, command: str):
        """
        This method is used to capture the logs from QNX port using given command
        :param command: Command need to be execute on the QNX port
        :type command: String
        """
        try:
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd='date -u "+Date: %d-%m-%Y Time: %H:%M:%S"')
            sleep(1)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=command)
            sleep(2)
        except Exception as exp:
            robot_print_error(
                f"Error to capture the qnx logs for command: {command}, EXCEPTION: {exp}",
                print_in_report=True)

    def capture_qnx_showmem_logs(self):
        """
        This method is used to execute the showmem -a command on the QNX terminal and save the logs into file

        This method create a thread and execute the command in given time interval. Time interval should
        be provided by the user in config file as "showMemACommandInterval".

        We will recommended to use more then 30 seconds to capture the data. As QNX memory not changed that
        frequently.

        :return: None
        :rtype: None
        """
        try:
            time_interval = self.config_manager.get_qnx_showmem_a_time_interval()
            command = self.config_manager.get_qnx_showmem_a_command()
            self.showmem_a_thread: threading.Timer = threading.Timer(
                interval=time_interval,
                function=self.capture_qnx_showmem_logs)
            self.showmem_a_thread.start()
            robot_print_debug(f"Capturing Showmem -a data")
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd='date -u "+showmem_a: %d-%m-%Y Time: %H:%M:%S"',
                                                     stop_prev=False)
            sleep(0.5)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=command,
                                                     stop_prev=False)
            sleep(7)
            if self.serial_logs.serial_thread.serial_logger.STOP_SERIAL_OPERATION:
                self.showmem_a_thread.cancel()
        except Exception as exp:
            robot_print_error(
                f"Error to capture the QNX showmem -a logs, EXCEPTION: {exp}",
                print_in_report=True)

    def stop_qnx_mem_logs(self, log_type):
        """
        This method is used to stop the QNX memory logs base on the log_type provided by the user.
        :param log_type: Type of the logs as below:
            1. for showmem -a: "a"
            2. for showmem -s : "s"
            3. for ufs(df -k) : "ufs"
        User doesn't need to take care of these argument as these are externally handle by the framework.
        :return: None
        """
        try:
            count = 1
            robot_print_info(f"Stop QNX logs call with argument: {log_type}",
                             print_in_report=True)
            if log_type == "a":
                self.showmem_a_thread.cancel()
                while self.showmem_a_thread.is_alive() and count == 10:
                    robot_print_debug(
                        f"It seems serial qnx mem log thread is still alive for {log_type} type. count: {count}")
                    self.showmem_a_thread.cancel()
                    count += 1
                robot_print_debug(
                    f"Serial qnx mem log thread stopped for type {log_type}")
            elif log_type == "s":
                self.showmem_s_thread.cancel()
                robot_print_info(
                    f"Stop qnx mem logs for thread: {self.showmem_s_thread}",
                    print_in_report=True)
                while self.showmem_s_thread.is_alive() and count == 10:
                    robot_print_debug(
                        f"It seems serial qnx mem log thread is still alive for {log_type} type. count: {count}")
                    self.showmem_s_thread.cancel()
                    count += 1
                robot_print_debug(
                    f"Serial qnx mem log thread stopped for type {log_type}")
            elif log_type == "ufs":
                self.ufs_thread.cancel()
            elif log_type == "slog2":
                self.slog_thread.cancel()
            else:
                raise Exception("Its seems android memory thread object either "
                                "not created or already destroyed")
        except Exception as exp:
            robot_print_error(
                f"Can't stop the android memory thread.\nEXCEPTION: %s" % exp)

    def start_qnx_showmem_summary_logs(self):
        """
        This method is used to capture the showmem -s logs from the QNX console.
        :return: None
        :rtype: None
        """
        try:
            time_interval = self.config_manager.get_qnx_showmem_s_time_interval()
            command = self.config_manager.get_qnx_showmem_s_command()
            self.showmem_s_thread: threading.Timer = threading.Timer(
                interval=time_interval,
                function=self.start_qnx_showmem_summary_logs)
            self.showmem_s_thread.start()
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd='date -u "+showmem_s: %d-%m-%Y Time: %H:%M:%S"',
                                                     stop_prev=False)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=command,
                                                     stop_prev=False)
            sleep(5)
        except Exception as exp:
            robot_print_error(
                f"Error to capture the showmem -s logs from qnx, EXCEPTION: {exp}",
                print_in_report=True)

    def start_qnx_ufs_data(self):
        """
        This method is used to capture the QNX UFS data by using df -k
        :return: None
        :rtype: None
        """
        try:
            time_interval = self.config_manager.get_qnx_ufs_time_interval()
            command = self.config_manager.get_qnx_ufs_command()
            self.ufs_thread: threading.Timer = threading.Timer(
                interval=time_interval,
                function=self.start_qnx_ufs_data)
            self.ufs_thread.start()
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd='date -u "+ufs: %d-%m-%Y Time: %H:%M:%S"')
            sleep(1)
            self.serial_logs.write_command_on_serial(device='qnx', cmd=command)
            sleep(2)
        except Exception as exp:
            robot_print_error(
                f"Error to capture the QNX UFC Data, EXCEPTION: {exp}",
                print_in_report=True)

    def precondition_for_slog2_busy_data(self):
        set_log_command = "echo gpu_set_log_level 4 > /dev/kgsl-control"
        gpu_stat_command = "echo gpubusystats 1000 > /dev/kgsl-control"
        self.serial_logs.write_command_on_serial(device='qnx',
                                                 cmd=set_log_command,stop_prev=False)
        sleep(2)
        self.serial_logs.write_command_on_serial(device='qnx',
                                                 cmd=gpu_stat_command, stop_prev=False)
        sleep(2)

    def start_slog2_busy_data(self):
        try:
            time_interval = self.config_manager.get_qnx_slog_interval()
            clear_log_command = "slog2info -c"
            slog_command = self.config_manager.get_qnx_slog2_command()
            ctrl_c_command = "\x03"
            self.slog_thread: threading.Timer = threading.Timer(
                interval=time_interval,
                function=self.start_slog2_busy_data)
            self.slog_thread.start()
            robot_print_debug(f"Capturing slog2 busy data")
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd='date -u "+slog: %d-%m-%Y Time: %H:%M:%S"',
                                                     stop_prev=False)
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd=clear_log_command,
                                                     stop_prev=False)
            sleep(5)
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd=slog_command,
                                                     stop_prev=False)
            sleep(2)
            self.serial_logs.write_command_on_serial(device='qnx',
                                                     cmd=ctrl_c_command,
                                                     stop_prev=False)
            if self.serial_logs.serial_thread.serial_logger.STOP_SERIAL_OPERATION:
                self.slog_thread.cancel()
        except Exception as exp:
            robot_print_error(
                f"Error to capture the QNX slog2 busy data logs, EXCEPTION: {exp}")
