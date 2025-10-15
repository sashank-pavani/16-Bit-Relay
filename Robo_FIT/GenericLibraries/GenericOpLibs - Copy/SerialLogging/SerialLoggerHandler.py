import os
from time import sleep

from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLogThread import SerialLogThread


class SerialLoggerHandler:
    """
    This is a interface for UserSerialLogging class
    """

    def __init__(self):
        """
        This constructor initialize the ConfigurationManager
        """
        self.serial_thread = SerialLogThread()

    def start_getting_serial_logs(self, device: str, file_name: str = None):
        """
        This method is used to start the Serial logger and save into file
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param file_name: Name of the file in which user want to save the logs
        :return: None
        :rtype: None
        """
        return self.serial_thread.start_serial_log_thread(device=device, file_name=file_name)

    def write_command_on_serial(self, device: str, cmd: str, stop_prev: bool = True):
        """
        This method is used to write data on serial. It will execute given command on serial
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param cmd: Command to be execute, for ex. ls, slog2info
        :type cmd: String
        :param stop_prev: Stop the previous command by sending Ctrl+c
        :type stop_prev: Bool
        :return: None
        :rtype: None
        """
        self.serial_thread.write_command_on_serial(device=device, cmd=cmd, stop_prev=stop_prev)

    def find_in_serial_logs(self, device: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to find any string on serial logs
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param expected_string: String which need to be find on serial
        :type expected_string: String
        :param timeout: Reading timeout in seconds
        :type timeout: Int
        :return: Ture if string found, Otherwise False
        :rtype: Boolean
        """
        return self.serial_thread.find_in_serial_logs(device=device, expected_string=expected_string, timeout=timeout)

    def find_data_in_serial_logfile(self, device: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to find any string on serial logs
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param expected_string: String which need to be find on serial
        :type expected_string: String
        :param timeout: Reading timeout in seconds
        :type timeout: Int
        :return: Ture if string found, Otherwise False
        :rtype: Boolean
        """
        return self.serial_thread.find_st(device=device, expected_string=expected_string, timeout=timeout)

    def rw_on_serial(self, device: str, cmd: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to write and read from serial. It will execute given command on serial
        and check given expected string found on serial or not.
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param cmd: Command which need to be execute
        :type cmd: String
        :param expected_string: String which need to find on serial logs
        :type expected_string: String
        :param timeout: Reading timeout in seconds
        :type timeout: Int
        :return: True if found otherwise False
        :rtype: Bool
        """
        return self.serial_thread.rw_on_serial(device=device, cmd=cmd, expected_string=expected_string, timeout=timeout)

    def read_from_serial_logs(self, device: str, cmd: str, timeout: int = 10):
        """
        This method read the string from serial logs.
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param cmd: Commend need to be execute
        :type cmd: String
        :param timeout: Reading Timeout in seconds
        :type timeout: Int
        :return: Read string
        :rtype: String
        """
        return self.serial_thread.read_from_serial_logs(device=device, cmd=cmd, timeout=timeout)

    def stop_getting_serial_log(self, device: str):
        """
        This method stop the serial logs and save the log
        :param device: Name of the device to stop log as per config file.
        :return: None
        """
        return self.serial_thread.stop_getting_serial_log(device)

    def remove_serial_connection(self, device: str):
        """
        This method is used to remove the serial connection
        :return: None
        """
        self.serial_thread.remove_serial_connection(device=device)

    def read_data_on_serial_logfile(self, device: str, expected_string: str):
        """
        This method is used to remove the serial connection
        :param device: Name of the device as per config
        :param expected_string : string that you want to search
        :param file_name : file name of the serial
        :type device: String
        :return: None
        :rtype: None
        """
        return self.serial_thread.read_data_on_serial_logfile(device=device, expected_string=expected_string,file_name=None)