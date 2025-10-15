import concurrent.futures
import sys
from time import sleep
import re
import time
from robot.api import logger
from serial import Serial, SerialTimeoutException, SerialException
import os
from queue import Queue
from datetime import datetime
from datetime import timedelta
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.serial_interface import _get_device_from_script

log_file = None


class SerialLogging:
    __is_closed = None
    __instance = None
    __instance_qnx = None
    __instance_vip = None
    __instance_tcu = None
    __instance_extra = None
    STOP_STATUS = None
    __is_loop_break = False
    __logfile_path = None
    __logfile_one = None
    __logfile_two = None
    __logfile_three = None
    __logfile_four = None
    __logfile_name: str = ""
    STOP_SERIAL_OPERATION = False
    __STOP_LOG_FOR_DEVICE = None

    @staticmethod
    def get_serial_instance() -> 'SerialLogging':
        """
        This method is to initialize the class only once.
        :param config_path: path of the serial configuration file
        :return : object of UserSerialLogging class
        """
        if SerialLogging.__instance is None:
            SerialLogging()
        return SerialLogging.__instance

    def __init__(self):
        try:
            # get the serial port path
            self.common_keyword = CommonKeywordsClass()
            self.config_manager = ConfigurationManager()
            SerialLogging.__instance = self
            self.queue = Queue()

        except ValueError as exp:
            robot_print_error("There is a exception to initialize the Serial and ISerialLogging, EXCEPTION : %s" % exp,
                              print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to initialize {__name__}, EXCEPTION: {exp}", print_in_report=True)

    def __get_serial_port_instance(self, device: str) -> Serial:
        """
        This Method is return the serial port instance
        :device: device name
        :return: Serial
        """
        try:
            if device.lower() == self.config_manager.get_serial_one_name():
                if SerialLogging.__instance_qnx is None:
                    SerialLogging.__instance_qnx = Serial(
                        port=_get_device_from_script(self.config_manager.get_serial_one_port()),
                        baudrate=self.config_manager.get_serial_one_baudrate(),
                        timeout=10)
                return SerialLogging.__instance_qnx
            elif device.lower() == self.config_manager.get_serial_two_name():
                if SerialLogging.__instance_vip is None:
                    SerialLogging.__instance_vip = Serial(
                        port=_get_device_from_script(self.config_manager.get_serial_two_port()),
                        baudrate=self.config_manager.get_serial_two_baudrate(),
                        timeout=10)
                return SerialLogging.__instance_vip
            elif device.lower() == self.config_manager.get_serial_three_name():
                if SerialLogging.__instance_tcu is None:
                    SerialLogging.__instance_tcu = Serial(
                        port=_get_device_from_script(self.config_manager.get_serial_three_port()),
                        baudrate=self.config_manager.get_serial_three_baudrate(),
                        timeout=10)
                return SerialLogging.__instance_tcu
            elif device.lower() == self.config_manager.get_serial_four_name():
                if SerialLogging.__instance_extra is None:
                    SerialLogging.__instance_extra = Serial(
                        port=_get_device_from_script(self.config_manager.get_serial_four_port()),
                        baudrate=self.config_manager.get_serial_four_baudrate(),
                        timeout=10)
                return SerialLogging.__instance_extra
            else:
                robot_print_error("Please enter valid device ID to access serial port", print_in_report=True)
                raise Exception()
        except Exception as exp:
            raise Exception(f"Please enter valid device ID to access serial port {exp}")

    def __create_serial_logfile(self, device: str, file_name: str = None):
        """
        This Method is used to crate the serial log file
        :param device: Name of the device, Should be same as given in config file
        :return: any or file according to instance
        """
        try:
            SerialLogging.__logfile_path = os.path.join(self.common_keyword.get_report_path(), "Serial_Logs")
            if not os.path.isdir(SerialLogging.__logfile_path):
                os.makedirs(SerialLogging.__logfile_path, mode=0o777)
                os.chmod(SerialLogging.__logfile_path, 0o777)
            if device.lower() == self.config_manager.get_serial_one_name():
                # creating the log file by using time and date to save the serial logs
                if SerialLogging.__logfile_one is None or SerialLogging.__logfile_one != file_name:
                    if file_name is None:
                        timestamp = time.strftime("%a_%d_%b_%Y_%I_%M_%S")
                        SerialLogging.__logfile_one = "{name}_Serial_Logs_{time}.log".format(
                            name=self.config_manager.get_serial_one_name(), time=timestamp)
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_one}",
                            print_in_report=True)
                    else:
                        SerialLogging.__logfile_one = f"{file_name}.log"
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in custom file name: {SerialLogging.__logfile_one}",
                            print_in_report=True)
                return SerialLogging.__logfile_one
            elif device.lower() == self.config_manager.get_serial_two_name():
                # creating the log file by using time and date to save the serial logs
                if SerialLogging.__logfile_two is None or SerialLogging.__logfile_two != file_name:
                    if file_name is None:
                        timestamp = time.strftime("%a_%d_%b_%Y_%I_%M_%S")
                        SerialLogging.__logfile_two = "{name}_Serial_Logs_{time}.log".format(
                            name=self.config_manager.get_serial_two_name(), time=timestamp)
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_two}",
                            print_in_report=True)
                    else:
                        SerialLogging.__logfile_two = f"{file_name}.log"
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_two}",
                            print_in_report=True)
                return SerialLogging.__logfile_two
            elif device.lower() == self.config_manager.get_serial_three_name():
                # creating the log file by using time and date to save the serial logs
                if SerialLogging.__logfile_three is None or SerialLogging.__logfile_three != file_name:
                    if file_name is None:
                        timestamp = time.strftime("%a_%d_%b_%Y_%I_%M_%S")
                        SerialLogging.__logfile_three = "{name}_Serial_Logs_{time}.log".format(
                            name=self.config_manager.get_serial_three_name(), time=timestamp)
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_three}",
                            print_in_report=True)
                    else:
                        SerialLogging.__logfile_three = f"{file_name}.log"
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_three}",
                            print_in_report=True)
                return SerialLogging.__logfile_three
            elif device.lower() == self.config_manager.get_serial_four_name():
                # creating the log file by using time and date to save the serial logs
                if SerialLogging.__logfile_four is None or SerialLogging.__logfile_four != file_name:
                    if file_name is None:
                        timestamp = time.strftime("%a_%d_%b_%Y_%I_%M_%S")
                        SerialLogging.__logfile_four = "{name}_Serial_Logs_{time}.log".format(
                            name=self.config_manager.get_serial_four_name(), time=timestamp)
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_four}",
                            print_in_report=True)
                    else:
                        SerialLogging.__logfile_four = f"{file_name}.log"
                        robot_print_debug(
                            f"Start getting serial logs for device : {device}, in file name: {SerialLogging.__logfile_four}",
                            print_in_report=True)
                return SerialLogging.__logfile_four
            else:
                raise Exception()
        except IOError as io_err:
            robot_print_debug("Error to create the Serial log file, %s" % io_err, print_in_report=True)
            return False

    def __open_serial_port(self, device: str) -> bool:
        """
        This method is used to check the serial is open or not
        Also if port is close the it try to open the serial port.
        :return: Boolean value, If port open return True otherwise False
        """
        try:
            port = self.__get_serial_port_instance(device)
            robot_print_debug(f"port={port}, device={device}")
            if port.isOpen():
                return True
            else:
                port.open()
                sleep(5)
                if port.isOpen():
                    return True
        except SerialException as serialexcep:
            robot_print_error("There is an error to open the serial port, EXCEPTION : %s" % serialexcep,
                              print_in_report=True)

    def convert_adb_to_usb(self) -> bool:
        """
        convert the adb to usb using serial interface
        :return: boolean value, True if successfully convert otherwise Flase
        """
        sleep(5)
        if self.__open_serial_port("qnx"):
            try:
                robot_print_debug("Converting ADB to USB, Please wait .....!!!! ", print_in_report=True)
                isSuccess = False
                sleep(0.5)
                sucmd = "su\n"
                self.__instance_qnx.write(sucmd.encode())
                sleep(5)
                convtcmd = "echo host > /sys/bus/platform/devices/a600000.ssusb/mode\n"
                self.__instance_qnx.write(convtcmd.encode())
                sleep(15)
                return True
            except SerialTimeoutException as serialerr:
                robot_print_debug(
                    "There is a error to write a command on serial terminal, Serial_Timeout_Exception.\n Exception "
                    ":  %s" % serialerr, print_in_report=True)
            except SerialException as exception:
                robot_print_debug(
                    "There is a error to write a command on serial terminal.\n Exception :  %s" % exception,
                    print_in_report=True)
        else:
            robot_print_error("Cannot open the port %s" % self.config_manager.get_serial_one_port(),
                              print_in_report=True)

    def convert_usb_to_adb(self) -> bool:
        """
        convert the adb to usb using serial interface
        :return: boolean value, True if successfully convert otherwise False
        """

        sleep(5)
        if self.__open_serial_port("one"):
            try:
                robot_print_debug("Converting USB to ADB, Please wait .....!!!!", print_in_report=True)
                sleep(5)
                sucmd = "su\n"
                self.__instance_qnx.write(sucmd.encode())
                sleep(5)
                cnvcmd = "echo peripheral > /sys/bus/platform/devices/a600000.ssusb/mode\n"
                self.__instance_qnx.write(cnvcmd.encode())
                sleep(15)
                return True
            except SerialTimeoutException as serialerr:
                robot_print_debug(
                    "There is a error to write a command on serial terminal, Serial_Timeout_Exception.\n Exception "
                    ":  %s" % serialerr, print_in_report=True)
            except SerialException as exception:
                robot_print_debug(
                    "There is a error to write a command on serial terminal.\n Exception :  %s" % exception)
        else:
            robot_print_error("Cannot open the port %s" % self.config_manager.get_serial_one_port(),
                              print_in_report=True)
        return False

    def write_command_on_serial(self, device: str, cmd: str, stop_prev: bool = True):
        """
        This method is used to write command on serial
        :param device: Name of the device, Should be same as given in config file
        :type device: String
        :param cmd: Command to be execute, for ex. ls, slog2info
        :type cmd: String
        :param stop_prev: Stop the previous command by sending Ctrl+c
        :type stop_prev: Bool
        :return: None
        :rtype: None
        """
        try:
            if self.__open_serial_port(device):
                port = self.__get_serial_port_instance(device)
                command = "\n" + cmd + "\n"
                if stop_prev:
                    robot_print_debug(f"Sending Ctrl+c on serial terminal to stop before running logs")
                    port.write("\x03".encode())
                    sleep(0.5)
                    port.write("\x03".encode())
                sleep(0.5)
                port.write(command.encode())
                sleep(2)
                sleep(0.1)
                robot_print_debug(f"{cmd}\tcommand write successfully", print_in_report=True)
            else:
                robot_print_debug("Serial port is close", print_in_report=True)
        except SerialTimeoutException as serial_time_exp:
            robot_print_debug("Error to write the command on serial, EXCEPTION: %s" % serial_time_exp,
                              print_in_report=True)
        except SerialException as serial_exp:
            robot_print_debug("Error to execute the serial command, EXCEPTION: %s" % serial_exp, print_in_report=True)

    def __write_on_serial(self, device: str, cmd: str):
        """
        This method is used to write data on serial. It will execute given command on serial
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param cmd: Command to be execute, for ex. ls, slog2info
        :type cmd: String
        :return: None
        :rtype: None
        """
        try:
            port = self.__get_serial_port_instance(device)
            if self.__open_serial_port(device):
                robot_print_debug("\nWrite command: %s" % cmd)
                cmd = "\n" + cmd + "\n"
                command = cmd.encode()
                robot_print_debug(f"Sending Ctrl+c on serial terminal to stop before running logs")
                port.write("\x03".encode())
                sleep(1)
                port.write(command)
                sleep(0.1)
                robot_print_debug(f"{cmd}\tcommand write successfully", print_in_report=True)
            else:
                robot_print_debug("Serial port is close", print_in_report=True)
        except SerialException as ser:
            robot_print_error("Error to write the command on serial, EXCEPTION: %s" % ser, print_in_report=True)

    def __find_serial_file(self, device: str):
        """
        This method is used to find the serial file
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :return: None
        :rtype: None
        """
        try:
            files = os.listdir(SerialLogging.__logfile_path)
            file_name = r"{device}(.)+".format(device=device)
            for file in files:
                if re.match(file_name, file):
                    return file
        except Exception as exp:
            robot_print_error(f"Error found on finding the serial logs , {exp}")
        return False

    def __find_on_serial(self, device: str, expected_string: str = "", timeout: int = 10):
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
        try:
            # check port is open
            if self.__open_serial_port(device):
                # stop getting serial log thread
                port = self.__get_serial_port_instance(device)
                sleep(2)
                end_time = datetime.now() + timedelta(seconds=timeout)
                # again same the file in append mode
                logfile_name = self.__create_serial_logfile(device)
                file_name = os.path.join(SerialLogging.__logfile_path, logfile_name)
                file = open(file_name, "a+")
                robot_print_debug("\nStart reading file to find the str", print_in_report=True)
                self.stop_file_writing(device, status=1)
                flag = False
                output_str = ""
                port.flushInput()
                port.flushOutput()
                while datetime.now() <= end_time:
                    # read the byte from the serial
                    byte_of_read = port.inWaiting()
                    # create the string from output bytes
                    output = (port.read(byte_of_read)).decode("utf-8")
                    # add into file
                    file.writelines(output)
                    # print("output is : ", output)
                    # compare the string
                    if expected_string != "" and expected_string in output:
                        flag = True
                        robot_print_info(f"String found : {output}")
                        # close the current file
                        file.close()
                        # start getting logs again
                        SerialLogging.STOP_STATUS = None
                        return True
                    elif expected_string == "" and len(output_str) > 100:
                        raise BufferError("output string size is more than buffer size")
                    output_str = output_str + output
                SerialLogging.STOP_STATUS = None
                robot_print_info("String not found after waiting %d" % timeout)
                robot_print_debug("String not found after waiting %d" % timeout)
                robot_print_debug(f"Output string is : {output_str}", print_in_report=True)
                if expected_string in output_str:
                    return True
                if not flag and expected_string == "":
                    robot_print_info("String not found after waiting %d" % timeout)
                    robot_print_debug("String not found after waiting %d" % timeout)
                    return False
            else:
                robot_print_debug("Serial port is close")
        except SerialException as ser:
            robot_print_error(f"Error to read the command on serial, EXCEPTION: {ser}")
            SerialLogging.STOP_STATUS = None

    def find_string_in_serial_file(self, device: str, expected_string: str):
        """
        find the string in serial file
        """
        logfile_name = self.__create_serial_logfile(device)
        robot_print_debug(f"Start reading serial logs for device : {device}, in file name: {logfile_name}")
        log_file_path = os.path.join(SerialLogging.__logfile_path, logfile_name)
        robot_print_debug(f"Start reading serial logs for device : {device}, in file path: {log_file_path}")
        serial_log_file = open(log_file_path, "r")
        try:
            if serial_log_file is not None:
                if expected_string in serial_log_file.read():
                    return True
            else:
                robot_print_error(f"Serial file is None for device : {device}, in file path: {log_file_path}")
                return False
        except FileNotFoundError as exp:
            robot_print_error(f"Serial file not found for device : {device}, in file path: {log_file_path} Exp : {exp}")
            return False
        except Exception as nexp:
            robot_print_error(f"Serial file not found for device : {device}, in file path: {log_file_path} Exp : {nexp}")
            return False
        finally:
            robot_print_debug("serial file close")
            serial_log_file.close()

    def __start_reading(self, device, expected_string: str = "", timeout: int = 10) -> concurrent.futures:
        """
        This method is used to start reading the given string in time
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param expected_string: String which need to be find on serial
        :type expected_string: String
        :param timeout: Reading timeout in seconds
        :type timeout: Int
        :return: result
        """
        executor = concurrent.futures.ThreadPoolExecutor()
        result = [executor.submit(self.__find_on_serial, device, expected_string, timeout)]
        return result

    def find_in_serial(self, device: str, expected_string: str, timeout: int = 10) -> concurrent.futures:
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
        try:
            ans = self.__start_reading(device, expected_string, timeout)
            sleep(2)
            for r in ans:
                if r.result():
                    robot_print_debug(f"String found, status {r.result()}", print_in_report=True)
                    return True
                else:
                    robot_print_debug(f"String not found, status {r.result()}", print_in_report=True)
                    return False
        except SerialException as serial_exp:
            robot_print_error(f"Error to find the {expected_string} on serial, EXCEPTION: {serial_exp}",
                              print_in_report=True)
            return False

    def read_from_serial_logs(self, device: str, cmd: str, timeout: int) -> any:
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
        try:
            out = self.__start_reading(device=device, timeout=timeout)
            sleep(10)
            robot_print_debug(f"Thread run completed....", print_in_report=True)
            self.__write_on_serial(device=device, cmd=cmd)
            # self.__write_on_serial(device=device, cmd="ls -l")
            for res in concurrent.futures.as_completed(out):
                robot_print_debug(f"Serial output for command: {res.result()}", print_in_report=True)
                return res.result()
        except BufferError as buffer_exp:
            raise BufferError(buffer_exp)
        except SerialException as ser:
            robot_print_error(f"Error to read the command on serial, EXCEPTION: {ser}", print_in_report=True)
            SerialLogging.STOP_STATUS = None

    def rw_serial_operation(self, device: str, cmd: str, expected_string: str, timeout: int):
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
        try:
            ans = self.__start_reading(device, expected_string=expected_string, timeout=timeout)
            sleep(5)
            self.__write_on_serial(device, cmd)
            for r in ans:
                res = r.result()
                if res:
                    robot_print_debug("PASS, r= %s" % str(res), print_in_report=True)
                    return res
                else:
                    robot_print_debug("FAIL, and r= %s " % str(res), print_in_report=True)
                    return res
        except SerialTimeoutException as serial_time_exp:
            robot_print_debug("Timeout to execute the command on serial, EXCEPTION: %s" % serial_time_exp,
                              print_in_report=True)
            raise SerialTimeoutException()
        except SerialException as serial_exp:
            robot_print_debug("Error to execute the command on serial, EXCEPTION: %s" % serial_exp,
                              print_in_report=True)
            raise SerialException()
        except Exception as exp:
            robot_print_debug("Error in execution, EXCEPTION: %s" % exp, print_in_report=True)
            raise Exception()

    def stop_file_writing(self, device: str, status=None) -> bool:
        """
        This class is used to Stop 'while loop' which used in writing file.
        :param status: set 1 if stop file writing, otherwise None.
        :param device: Name of the device to stop log as per config file.
        :return: bool value, True if status is not none otherwise False.
        """
        SerialLogging.STOP_STATUS = status
        SerialLogging.__is_closed = status
        SerialLogging.__STOP_LOG_FOR_DEVICE = device
        # self.remove_serial_connection(device=device)
        try:
            if SerialLogging.STOP_STATUS is not None:
                robot_print_info(f"SERIAL STOP STATUS, status: {SerialLogging.STOP_STATUS}", print_in_report=True)
                sleep(2)
                return SerialLogging.__is_loop_break
        except Exception as exp:
            robot_print_error(f"Error to stop serial file writing : {exp}")
        return False

    def write_to_file(self, device: str, file_name: str = None, queue: Queue = None):
        """
        This method is used to write serial data on file
        :param device: Name of the device, Should be same as given in config file
        For more please check online doc.
        :type device: String
        :param file_name: file name in which write serial data
        :param queue: queue object of Class Queue
        :type file_name: None
        :return: None
        :rtype: None
        """
        robot_print_debug("Start getting Queue data", print_in_report=True)
        serial_log_file = None
        try:
            # creating the directory for saving the serial logs
            robot_print_debug("Start getting Queue data", print_in_report=True)
            logfile_name = self.__create_serial_logfile(device, file_name=file_name)
            robot_print_debug(f"Start getting serial logs for device : {device}, in file name: {logfile_name}")
            log_file_path = os.path.join(SerialLogging.__logfile_path, logfile_name)
            robot_print_debug(f"Start getting serial logs for device : {device}, in file path: {log_file_path}")
            # open the file and start to write the file
            serial_log_file = open(log_file_path, "a+")
            SerialLogging.__is_closed = None
            end_time = datetime.now() + timedelta(seconds=10)
            while True:
                try:
                    while not queue.empty():
                        try:
                            serial_log_file.write(f"{queue.get().decode('utf-8')}")
                        except UnicodeDecodeError as decode_err:
                            if "'utf-8' codec can't decode byte 0xf0" in str(decode_err):
                                robot_print_debug("Encoding Error Handling Called here...")
                                serial_log_file.write(f"{queue.get().decode('latin-1')}")
                        finally:
                            if datetime.now() >= end_time:
                                serial_log_file.flush()
                                os.fsync(serial_log_file.fileno())
                                end_time = datetime.now() + timedelta(seconds=10)
                    if SerialLogging.__is_closed is not None:
                        robot_print_debug("write to file is stop", print_in_report=True)
                        SerialLogging.STOP_STATUS = None
                        SerialLogging.__is_closed = None
                        break
                except Exception as exp:
                    robot_print_debug("Error in while loop, %s" % exp)
        except Exception as io_err:
            robot_print_debug("Error to create the Serial log file, %s" % io_err)
        finally:
            robot_print_debug("close file")
            serial_log_file.close()

    def start_getting_serial_logs(self, device: str, queue: Queue):
        """
        This file is used to Write the serial logs into the file.
        Location of file -> /<framework_path>/Test_Reports/<Project_date_time>/Test/Serial_Log/<seriallogsfile>.log
        :param queue: queue object of Class Queue
        :return: none
        """
        try:
            # global log_file
            # robot_print_debug("Start getting Queue data", print_in_report=True)
            if self.__open_serial_port(device):
                SerialLogging.STOP_SERIAL_OPERATION = False
                # creating the directory for saving the serial logs
                port = self.__get_serial_port_instance(device)
                SerialLogging.STOP_STATUS = None
                while True:
                    try:
                        if port.in_waiting > 0:
                            byte_to_read = port.inWaiting()
                            # print("Byte to be read: ", port.read(byte_to_read))
                            queue.put(port.read(byte_to_read))
                        if SerialLogging.STOP_STATUS is not None and SerialLogging.__STOP_LOG_FOR_DEVICE == device:
                            SerialLogging.STOP_STATUS = None
                            SerialLogging.STOP_SERIAL_OPERATION = True
                            SerialLogging.__is_loop_break = True
                            robot_print_info(f"Closing while loop for {device}")
                            break
                    except Exception as exp:
                        robot_print_error(f"Error to read the serial logs, EXCEPTION: {exp}")
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        robot_print_debug(f"{exc_type}, {file_name}, {exc_tb.tb_lineno}")
                robot_print_debug(f"Closing serial port {device} : {port}", print_in_report=True)
            else:
                robot_print_debug("Serial port is close, Please Check the port ", print_in_report=True)
        except SerialException as serialexep:
            robot_print_error("Error to write the serial logs into the file, EXCEPTION: %s" % serialexep,
                              print_in_report=True)
        except OSError as oserr:
            robot_print_error("Error to create the Serial Log Folder, EXCEPTION : %s" % oserr, print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error in start getting serial logs, EXCEPTION: {exp}", print_in_report=True)

    def remove_serial_connection(self, device: str):
        """
        This method is used to remove the connection and close the log file
        :return: none
        """
        try:
            global log_file
            port = self.__get_serial_port_instance(device)
            if port.isOpen():
                port.close()
                robot_print_debug("Serial Close...!!!")
            else:
                robot_print_debug("Serial Close Failed")
        except SerialException as serialerr:
            robot_print_error("There is an error to close the serial port, EXCEPTION : %s " % serialerr,
                              print_in_report=True)
        except IOError as ioerr:
            robot_print_error("There is an error to close the serial log file, EXCEPTION: %s" % ioerr,
                              print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to remove serial connection, EXCEPTION :{exp}", print_in_report=True)
