import concurrent.futures
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from time import sleep
from concurrent.futures import Future
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLogging import SerialLogging
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug, robot_print_error, \
    robot_print_info


@dataclass
class ThreadRegister:
    start_thread: Future
    write_thread: Future
    start_thread_status: bool
    write_thread_status: bool


class SerialLogThread:
    """
    This class is create the thread for Serial Logging
    """

    __THREAD_REGISTER_DATA = {}

    def __init__(self):
        try:
            self.thread = ThreadPoolExecutor(max_workers=5)
            self.serial_logger = SerialLogging.get_serial_instance()
            self.start_thread = None
            self.write_thread = None
        except Exception as exp:
            robot_print_error(f"Error to initialize Serial Logging thread class, EXCEPTION: {exp}")

    def __register_threads(self, device_name: str, data: ThreadRegister):
        """
        This function will use to register the thread, so that only one time thread can start for each device
        User should have to stop the thread first before running it again.
        :param device_name: Name of the device for which thread is running
        :type device_name: String
        :param data: Data which is required
        :type data: ThreadRegister
        :return: None
        :rtype: None
        """
        try:
            SerialLogThread.__THREAD_REGISTER_DATA[device_name] = data
        except Exception as exp:
            robot_print_error(f"Error to register the thread, EXCEPTION {exp}")

    def __check_is_thread_already_running(self, device_name: str) -> bool:
        """
        The Function is used to check that thread is already running for the give device or not.
        :param device_name: Name of the device for user wants to check the thread status
        :type device_name: String
        :return: True is thread is running, otherwise False
        :rtype: bool
        """
        try:
            data = SerialLogThread.__THREAD_REGISTER_DATA[device_name]
            if isinstance(data, ThreadRegister):
                if data.start_thread_status and data.write_thread_status:
                    robot_print_info(f"It seems threads are already running")
                    robot_print_debug(f"start thread = {data.start_thread.running()}")
                    robot_print_debug(f"write thread = {data.write_thread.running()}")
                    return True
                robot_print_info(f"It seems either of threads are not running")
                robot_print_debug(f"start thread = {data.start_thread.running()}")
                robot_print_debug(f"write thread = {data.write_thread.running()}")
                return False
        except KeyError as key_error:
            robot_print_debug(f"It seems {device_name} is not registered in the thread record, EXCEPTION: {key_error}")
            return False
        except Exception as exp:
            robot_print_error(f"Error to check the record of the thread, EXCEPTION: {exp}")
            return False

    def start_serial_log_thread(self, device: str, file_name: str = None):
        """
        This method is used to start the serial logs.
        :param device: Name of the device as same pass in config file. Please check documentation for more details
        :type device: String
        :param file_name: Name of the file in which user want to save the logs
        :return: None
        :rtype: None
        """
        try:
            end_time = datetime.now() + timedelta(minutes=2)
            flg = {"write": False, "start": False}
            queue = Queue()
            if not self.__check_is_thread_already_running(device_name=device):
                self.start_thread: Future = self.thread.submit(self.serial_logger.start_getting_serial_logs,
                                                               device, queue)
                self.write_thread: Future = self.thread.submit(self.serial_logger.write_to_file, device, file_name,
                                                               queue)
                robot_print_debug(f"Serial threads starting....\t{flg}")
                while end_time > datetime.now() and flg["start"] == False:
                    robot_print_debug(f"Status  {self.start_thread.running()}")
                    if not self.start_thread.running():
                        robot_print_debug("Serial Logs thread starting....")
                        flg["start"] = False
                    else:
                        flg["start"] = True
                    sleep(5)
                while end_time > datetime.now() and flg["write"] == False:
                    robot_print_debug(f"Status  {self.write_thread.running()}")
                    if not self.write_thread.running():
                        robot_print_debug("Serial Write thread starting....")
                        sleep(5)
                        flg["write"] = False
                    else:
                        flg["write"] = True
                    sleep(5)
                if flg["start"] == False or flg["write"] == False:
                    robot_print_debug("Serial threads not started, due to some error, Please check the logs!!!")
                    return False
                robot_print_debug(
                    f"Serial threads started!!!, start={self.start_thread.running()}, write={self.write_thread.running()}")
                # registering the thread
                self.__register_threads(device_name=device,
                                        data=ThreadRegister(start_thread=self.start_thread,
                                                            write_thread=self.write_thread,
                                                            start_thread_status=flg["start"],
                                                            write_thread_status=flg['write']))
                return True
            return False
        except Exception as exp:
            robot_print_error(f"Error to start getting serial logs, EXCEPTION: {exp}",
                              print_in_report=True)
            return False

    def stop_getting_serial_log(self, device: str):
        """
        This method is used to stop serial log from thread
        :param device: Name of the device to stop log as per config file.
        """
        try:
            is_file_stop = self.serial_logger.stop_file_writing(device, 1)
            if is_file_stop:
                while self.start_thread is not None and self.start_thread.running():
                    robot_print_debug("Closing Serial Start log thread....")
                    self.start_thread.done()
                    # self.start_thread.cancel()
                    self.serial_logger.stop_file_writing(device, 1)
                    sleep(5)
                while self.write_thread is not None and self.write_thread.running():
                    robot_print_debug("Closing Serial write file thread....")
                    self.write_thread.done()
                    # self.start_threat.cancel()
                    self.serial_logger.stop_file_writing(device, 1)
                    sleep(5)
                self.__register_threads(device_name=device,
                                        data=ThreadRegister(start_thread=self.start_thread,
                                                            write_thread=self.write_thread,
                                                            start_thread_status=False,
                                                            write_thread_status=False))
                robot_print_debug(f"Serial logs stop now", print_in_report=True)
                return True
            else:
                robot_print_debug(f"Serial logs file not Stop: is_file_stop: {is_file_stop}", print_in_report=True)
                return False
        except Exception as exp:
            robot_print_error(f"Error to stop the serial logs, EXCEPTION: {exp}", print_in_report=True)
            return False

    def write_command_on_serial(self, device: str, cmd: str, stop_prev: bool = True):
        """
        This method is used to write the command on serial, user can execute given command on serial.
        :param device: Name of the device as per config file.
        :type device: String
        :param cmd: Command to be execute
        :type cmd: String
        :param stop_prev: Stop the previous command by sending Ctrl+c
        :type stop_prev: Bool
        :return: None
        :rtype: None
        """
        self.serial_logger.write_command_on_serial(device=device, cmd=cmd, stop_prev=stop_prev)

    def find_in_serial_logs(self, device: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to find any data on serial.
        :param device: Name of the device as per config
        :type device: String
        :param expected_string: String which is expected
        :type expected_string: String
        :param timeout: Time interval for read the logs
        :type timeout: int
        :return: True if expected string found otherwise False
        :rtype: Bool
        """
        try:
            output = self.serial_logger.find_in_serial(device=device, expected_string=expected_string,
                                                       timeout=timeout)
            if self.start_thread is not None:
                if not self.start_thread.running():
                    robot_print_debug(f"Serial logs thread stopped, Running Again", print_in_report=True)
                    self.start_serial_log_thread(device=device)
                    sleep(5)
                    if self.start_thread.running():
                        robot_print_debug(f"Serial Thread running again", print_in_report=True)
            else:
                robot_print_debug(f"Serial logs thread is None. So, try to running Again", print_in_report=True)
                self.start_serial_log_thread(device=device)
                if self.start_thread.running():
                    robot_print_debug(f"Serial Thread running again", print_in_report=True)
            return output
        except Exception as exp:
            robot_print_error(f'Error in find on serial, EXCEPTION: {exp}', print_in_report=True)

    def rw_on_serial(self, device: str, cmd: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to read and write the data from the serial
        :param device: name of the device as per config
        :type device: String
        :param cmd: Command to be execute
        :type cmd: String
        :param expected_string: String which is expected
        :type expected_string: String
        :param timeout: Time interval for read the logs
        :type timeout: int
        :return: True if expected string found otherwise False
        :rtype: Bool
        """
        try:
            output = self.serial_logger.rw_serial_operation(device=device, cmd=cmd, expected_string=expected_string,
                                                            timeout=timeout)
            if self.start_thread is not None:
                if not self.start_thread.running():
                    robot_print_debug(f"Serial logs thread stopped, Running Again", print_in_report=True)
                    self.start_serial_log_thread(device=device)
                    sleep(5)
                    if self.start_thread.running():
                        robot_print_debug(f"Serial Thread running again", print_in_report=True)
            else:
                robot_print_debug(f"Serial logs thread is None. So, try to running Again", print_in_report=True)
                self.start_serial_log_thread(device=device)
                if self.start_thread.running():
                    robot_print_debug(f"Serial Thread running again", print_in_report=True)
            return output
        except Exception as exp:
            robot_print_error(f"Error in read write on serial, EXCEPTION: {exp}", print_in_report=True)

    def read_from_serial_logs(self, device: str, cmd: str, timeout: int = 0) -> str:
        """
        This method is used to read the serial logs
        :param device: Name of the device as per config
        :type device: String
        :param cmd: Command to be execute
        :type cmd: String
        :param timeout: Time interval for read logs
        :type timeout: Int
        :return: String values of logs
        :rtype: String
        """
        try:
            output = self.serial_logger.read_from_serial_logs(device=device, cmd=cmd,
                                                              timeout=timeout)
            if self.start_thread is not None:
                if not self.start_thread.running():
                    robot_print_debug(f"Serial logs thread stopped, Running Again", print_in_report=True)
                    self.start_serial_log_thread(device=device)
                    sleep(5)
                    if self.start_thread.running():
                        robot_print_debug(f"Serial Thread running again", print_in_report=True)
            else:
                robot_print_debug(f"Serial logs thread is None. So, try to running Again", print_in_report=True)

            return output
        except Exception as exp:
            robot_print_error(f"Error to read form the serial, EXCEPTION: {exp}", print_in_report=True)

    def remove_serial_connection(self, device: str):
        """
        This method is used to remove the serial connection
        :param device: Name of the device as per config
        :type device: String
        :return: None
        :rtype: None
        """
        self.serial_logger.remove_serial_connection(device=device)

    def read_data_on_serial_logfile(self, device: str, expected_string: str, file_name: str):
        """
        This method is used to search given data on serial log file
        :param device: Name of the device as per config
        :param expected_string : string that you want to search
        :param file_name : file name of the serial
        :type device: String
        :return: True if str found
        :rtype: Bool
        """
        return self.serial_logger.find_string_in_serial_file(device=device, expected_string=expected_string)
