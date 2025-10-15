import sys
import time
import subprocess
import shutil
import os
import re
from typing import Tuple, Union
from datetime import datetime
from ppadb.client import Client as ADBClient
from Robo_FIT.GenericLibraries.GenericOpLibs.ADBLogger.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.UserXmlReporting import UserXmlReporting
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_warning
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.ADBLogger.ADBConnectionFile import ADBConnectionFile
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager

STARTTIME = ""
ENDTIME = ""
VTYPE = ""
PID = 0
TIMESTAMP = ""
my_object: object = None

# count variable for save ignition log file
COUNT = 0


class ADBLoggerClass:
    """
    This class in responsible to handle the ADB logging and ADB shell command executions
    """
    _DEVICE = ""
    _ENABLED = ""

    __ADB_LOGCAT_FILE_NAME = None

    def __init__(self):
        """
        Constructor of ADBLoggerClass
        """
        self.config_manager = ConfigurationManager()
        self.common_keywords = CommonKeywordsClass()
        self.adb = ADBConnectionFile()
        self.project_config_manager = ProjectConfigManager()

        if ADBLoggerClass._ENABLED == "":
            ADBLoggerClass._ENABLED = self.config_manager.get_enabled_status()
        self.enabled = ADBLoggerClass._ENABLED

        if ADBLoggerClass._DEVICE == "":
            ADBLoggerClass._DEVICE = self.__get_device()
        self.device_name = ADBLoggerClass._DEVICE
        client = ADBClient(host='127.0.0.1', port=5037)
        try:
            self.device = client.device(ADBLoggerClass._DEVICE)
            self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")
        except Exception as excp:
            robot_print_error(f"It seems device is offline, EXCEPTION: {excp}")
            raise Exception(" Device is not available. Please check configuration file")

    def __get_device(self) -> str:
        """
        get device name according to adb usb id or network id provided in configuration file
        :return: device name
        """
        network_id = self.config_manager.get_adb_network_id()
        usb_id = self.config_manager.get_adb_usb_id()

        device_list = self.adb.get_devices_list()
        if network_id != "":
            if network_id in device_list:
                return network_id
        if usb_id != "":
            if usb_id in device_list:
                return usb_id
        else:
            robot_print_error("Please mention adb Device Id and Network Id in ADB Configuration File")
            return ""

    def check_device_status(self) -> bool:
        """
        This function responsible to return the status of the ADB device.
        :return: If device is connected and online then it will return True else false
        :rtype: bool
        """
        try:
            adb_device_list = self.adb.get_devices_list()
            if self.device_name not in adb_device_list:
                robot_print_warning(f"Given '{self.device_name}' device is offline.", print_in_report=True,
                                    underline=True)
                return False
            else:
                self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")
                return True
        except RuntimeError as run_err:
            robot_print_error(f"It seems given device {self.device_name} is offline, EXCEPTION: {run_err}'",
                              print_in_report=True)
            return False
        except Exception as exp:
            robot_print_error(f"Error to check the device status, EXCEPTION: {exp}", print_in_report=True
                              )
            return False

    def __get_command_output(self, command: str) -> str:
        """
        this function will return the given command output
        :param command: Command to be executed
        :type command: string
        :return: return the command output
        :rtype: bytes
        """
        return os.popen(command).read()

    def config_start_time(self):
        """
        This function is used handle the start time of the execution.
        :return: None
        :rtype: None
        """
        global STARTTIME
        try:
            if not self.check_device_status():
                STARTTIME = "Device Offline"
            else:
                STARTTIME = self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")
        except RuntimeError as run_err:
            robot_print_error(f"It seems given device {self.device_name} is offline, EXCEPTION: {run_err}'",
                              print_in_report=True)
            STARTTIME = "Device Offline"
        except Exception as exp:
            robot_print_error(f"Error while saving start time of {self.device_name} device, EXCEPTION: {exp}'",
                              print_in_report=True)
            STARTTIME = exp

    def config_log_type(self) -> bool:
        """
        This function configure the ADB log type. Logs should be mentioned in adblogger_configuration_file.json.
        To take the logs test case wise use  "type":"TESTCASEWISE" and for suite wise use "type":"ALLLOGS"
        :return: True if ALLLOGS else False
        :rtype: Bool
        """
        try:
            var = self.config_manager.get_log_type()
            if var.upper() == "ALLLOGS":
                return True
            elif var.upper() == "TESTCASEWISE":
                return False
        except ValueError as ve:
            robot_print_error(f"Please Configure the log type into configuration file, ERROR:  {ve}",
                              print_in_report=True)

    def save_time(self, testcase_name: str, test_status) -> None:
        """
        This will save the test case status and test case end time if test case is related to ADB handling
        :param testcase_name: Name of the test case
        :type testcase_name: String
        :param test_status: Status of the test case
        :type test_status: String
        :return: None
        :rtype: None
        """
        global STARTTIME, ENDTIME
        xml_reporting = UserXmlReporting()
        try:
            ENDTIME = self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")
            xml_reporting.xml_add_adb_test_cases_data(test_case_name=testcase_name, start_time=STARTTIME.strip(),
                                                      end_time=ENDTIME.strip(), status=test_status)
        except Exception as exp:
            robot_print_error(f"It seems given device {self.device_name} is offline, EXCEPTION: {exp}'")
            xml_reporting.xml_add_adb_test_cases_data(test_case_name=testcase_name, start_time=STARTTIME.strip(),
                                                      end_time=str(exp), status=test_status)

    def config_verbosity(self, verbosity_type: str):
        """
        This function is used to set the verbosity of the ADB loger
        :param verbosity_type: Type of verbosity
        :type verbosity_type: String
        :return: None
        :rtype: None
        """
        global VTYPE
        VTYPE = self.config_manager.get_by_type(verbosity_type.lower())
        print(VTYPE)

    def config_by_pid(self, package_name: str):
        """
        This function is set the configuration for ADB logger to take logs for perticulat PID
        It will get the PID of given package_name.
        :param package_name: Name of the package whose logs need to be monitored
        :type package_name: String
        :return: None
        :rtype: None
        """
        global PID
        get_pid_command = "adb shell ps | grep {packagename}".format(packagename=package_name)
        pid_list = self.__get_command_output(get_pid_command)
        PID = pid_list.split()[1]

    def __get_adb_logs(self, file_path: str, logcat_cmd: str):
        """
        This function collect the adb logs base of the give command and save into give file_path
        :param file_path: Path of the file in which logs need to be saved
        :type file_path: String
        :param logcat_cmd: Command which need to be executed for taking adb logs
        :type logcat_cmd: String
        :return: None
        :rtype: None
        """
        try:
            if self.check_device_status():
                ADBLoggerClass.__ADB_LOGCAT_FILE_NAME = file_path
                with open(file_path, "a+", encoding='utf-8', errors='replace') as fp:
                    process = subprocess.Popen(['adb', '-s', self.device_name, 'logcat', logcat_cmd],
                                               stderr=subprocess.PIPE,
                                               stdout=fp)
                    time.sleep(0.5)
                    process.communicate()
                    fp.close()
        except Exception as exp:
            robot_print_error("Error to get adb logs: %s" % exp, print_in_report=True)

    def __save_logs(self, testcase: str):
        """
        This file is used to save the adb logs
        and ignition cycle logs bases on the user configuration i.e. Test case failed or All logs
        :param testcase: name of the test case
        :return: none
        """
        global TIMESTAMP, VTYPE, PID
        file_path = os.path.join(self.common_keywords.get_log_screenshot_directory(testcase),
                                 "{filename}.log".format(filename=testcase.split(" ")[0]))

        if VTYPE != "":
            self.__get_adb_logs(file_path=file_path, logcat_cmd="-d *:{verbosity_type}".format(verbosity_type=VTYPE))
        elif PID != 0:
            self.__get_adb_logs(file_path, "--pid={user_pid}".format(user_pid=PID))
        else:
            self.__get_adb_logs(file_path, "-d")

    def __get_all_logs(self, suit_name: str) -> None:
        """
        This function will save all the suite wise logs into the file with give suite name
        :param suit_name: Name of the suite which is used to create the filename
        :type suit_name:
        :return: None
        :rtype: None
        """
        file_path = os.path.join(self.common_keywords.get_logs_screenshot_path(),
                                 "{filename}.log".format(filename=suit_name.split(".")[2]))
        self.__get_adb_logs(file_path=file_path, logcat_cmd="-d")

    def get_ignition_log(self, testcase_name: str) -> bool:
        """
        This method take the ignition test case logs
        :param testcase_name: Name of the test case which is used to save the logs and create file name
        :type testcase_name: String
        :return: None
        :rtype: None
        """
        try:
            global COUNT
            if ADBLoggerClass.__ADB_LOGCAT_FILE_NAME is None:
                ADBLoggerClass.__ADB_LOGCAT_FILE_NAME = os.path.join(
                    self.common_keywords.get_log_screenshot_directory(testcase_name),
                    "{filename}.log".format(filename=testcase_name.split(" ")[0]))

            try:
                self.__get_adb_logs(file_path=ADBLoggerClass.__ADB_LOGCAT_FILE_NAME, logcat_cmd="-d")
                xml_reporting = UserXmlReporting()
                xml_reporting.xml_add_ignition_data(test_case_name=testcase_name.split(" ")[0], start_time=(
                    self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")).strip(),
                                                    log_file_name=os.path.basename(
                                                        ADBLoggerClass.__ADB_LOGCAT_FILE_NAME))
                return True
            except IOError as io:
                robot_print_error(f"File does not exist: {io}", print_in_report=True)
                return False
        except OSError as oserr:
            robot_print_error(f"OSException : {oserr}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, file_name, exc_tb.tb_lineno)
            return False
        except ValueError as exception:
            robot_print_error(f"There is an Error to get the logs over ignition cycle, EXCEPTION: {exception}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, file_name, exc_tb.tb_lineno)
            return False

    def save_ignition_log_files(self, testname: str) -> bool:
        """
        This method save the ignition logs into the destination location.
        :param testname: name of the test case i.e. failed test case name
        :return: If move successfully return True, otherwise False
        """
        try:
            time.sleep(5)
            source_path = self.common_keywords.get_custom_ign_report_path(testname)
            destination_path = self.common_keywords.get_log_screenshot_directory(testname)
            print("PATH are : " + source_path + "  " + destination_path)
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)
                print("File Move successfully")
                return True
            else:
                robot_print_error("Error to move the file", print_in_report=True)
                return False
        except IOError as ioerr:
            robot_print_error(
                f"There is an error to move the Ignition files to Destination location : Exception {ioerr}",
                print_in_report=True)
            return False

    def get_test_logs(self, test_case_name: str):
        """
        This method is used to get the ADB log test case wise
        :param test_case_name: name of test case
        :return: None
        """
        if self.enabled:
            is_type = self.config_log_type()
            if not is_type:
                self.__save_logs(test_case_name)

    def get_suit_logs(self, suit_name: str):
        """
        This method is used to get the ADB log suit wise.
        :param suit_name: name of suit
        :return: None
        """
        if self.enabled:
            is_type = self.config_log_type()
            if is_type:
                self.__get_all_logs(suit_name)

    def capture_screenshot(self, test_case_name: str):
        """
        This method is used to capture the screenshot
        :param test_case_name: name of the test case, so the we can create the name of
        file according to test case name id
        :return: NONE
        """
        try:
            if self.check_device_status():
                screenshot_name = self.common_keywords.get_screenshot_path(test_case_name)
                with open(screenshot_name, "wb") as img_file:
                    img_file.write(self.device.screencap())
        except OSError as os_err:
            robot_print_error(f"There is an exception to capture screenshot, EXCEPTION: {os_err}", print_in_report=True)
        except RuntimeError as run_err:
            robot_print_error(
                f"It seemed {self.device_name} device is offline so not able to take screenshot, EXCEPTION: {run_err}",
                print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to capture the screenshot, EXCEPTION: {exp}", print_in_report=True)

    def get_android_boot_kpi_value(self):
        """
        This method is used to get the boot KPI value.
        After capture the KPI values it store into
        <root_path>/Test_Report/<project>_<date>_<time>/PerformanceUtilisation/BootKpiValue/BootKpiValue.log
        :return: None
        """
        try:
            path = self.common_keywords.performance_utilization_custom_path(ROBO_BOOT_KPI_DIR_NAME)
            time.sleep(0.5)
            path = os.path.join(path, ROBO_BOOT_KPI_FILE_NAME)
            boot_cmd = self.project_config_manager.get_boot_kpi_command()
            robot_print_debug(f"Boot KPI value, {path}", print_in_report=True)
            with open(path, "a+") as fp:
                fp.writelines(f"\nTime:{datetime.now().strftime('%H_%M_%S')}\n")
                fp.writelines(self.device.shell(boot_cmd))
                fp.writelines(f"\n\n")
                fp.close()
                robot_print_info(f"Capture Android KPI value at path: {path}", print_in_report=True)
        except IOError as io_err:
            robot_print_error(f"Error to get the ADB KPI value, EXCEPTION: {io_err}", print_in_report=True)
        except RuntimeError as run_err:
            robot_print_error(f"It seems device offline, EXCEPTION: {run_err}", print_in_report=True)

    def find_on_adb_output(self, cmd: str, expected_string: str, timeout: int = 10) -> bool:
        """
        This method is used to find the expected string in ADB command output.
        also it write the output in one file with command name and timestamp.
        Path for save the logs:
        <root_path>/Test_Reports/<project_folder_name>/Logs_Screenshot/ADB_Command_Data/adb_command_logs.log
        :param cmd: Command to be execute
        :param expected_string: String to be expected
        :param timeout: Wait time in which string is expected
        :return True if expected string found otherwise False.
        """
        file = None
        try:
            file_path = os.path.join(self.common_keywords.get_adb_command_data_file_path(),
                                     ROBO_ADB_CMD_SAVE_FILE_NAME)
            file = open(file_path, "a+")
            # TODO: if timeout requirement comes
            # end_time = datetime.now() + timedelta(seconds=timeout)
            try:
                if cmd != "" and expected_string != "":
                    adb_time = self.device.shell("date +\"%m-%d %H:%M:%S.%3N\"")
                    file.write(f"Command: {cmd}\nADB Timestamp: {adb_time}\n")
                    out = (self.device.shell(cmd)).split("\n")
                    for val in out:
                        print(val)
                        if expected_string in val:
                            file.write(str(val) + "\n")
                            file.write("\n\n\n\n")
                            file.close()
                            return True
                        file.write(str(val) + "\n")
                    file.write("\n\n\n\n")
                    file.close()
                    return False
                else:
                    robot_print_error(
                        f"You have not provide either command or expected string."
                        f" Please check the arguments.\nCommand={cmd}\nExpected String={expected_string}\n",
                        print_in_report=True)
                    file.close()
                    return False
            except RuntimeError as run_exp:
                robot_print_error(
                    f"ADB device offline or not connected with system,'"
                    f" Please check the ADB coonnection by using 'adb devices'. EXCEPTION: {run_exp}",
                    print_in_report=True)
                file.close()
                return False
        except IOError as io_err:
            robot_print_error(f"There is an error to write the logs in file, EXCEPTION: {io_err}",
                              print_in_report=True)
            file.close()
            return False

    def execute_adb_command(self, cmd: str):
        """
        This method just execute the ADB command on ADB console. No output will we return.
        :param cmd: Command to be execute
        :return: None
        """
        try:
            if self.check_device_status():
                robot_print_debug(f"Start executing the command: {cmd}")
                out = self.device.shell(cmd)
                robot_print_info(f"Command Execute: {cmd},\nResult: {out}")
        except RuntimeError as exp:
            robot_print_error(f"It seems device is offline: '{cmd}', EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Error to execute the command on ADB console: '{cmd}', EXCEPTION: {exp}")

    def push_file_inside_adb(self, src_path, des_path) -> bool:
        """
        THis function is used to push the file inside the Android file system.
        It will root and remount the device before pushing the file. So be care full to call the method.
        :param src_path: Source file path (Path of file which need to be pushed)
        :type src_path: String
        :param des_path: Destination file path in which file need to be pushed (Path of Android File System)
        :type des_path: String
        :return: True if pushed successfully otherwise False
        :rtype: bool
        """
        try:
            if self.check_device_status():
                try:
                    out = subprocess.Popen(f"adb -s {self.device_name} root", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    out = subprocess.Popen(f"adb -s {self.device_name} remount", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    out = subprocess.Popen(f"adb -s {self.device_name} push {src_path} {des_path}", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    if "1 file pushed" in str(out):
                        return True
                except OSError as os_err:
                    robot_print_error(f"Error to push the file: {src_path} inside : {des_path}, EXCEPTION: {os_err}")
            robot_print_error(f"It seems device: {self.device_name} is offline and RoboFIT not able to push the file",
                              print_in_report=True)
            return False
        except Exception as exp:
            robot_print_error(f"Error to push the file inside the ADB device: {self.device_name}, EXCEPTION: {exp}",
                              print_in_report=True)

    def pull_file_from_adb(self, src_path: str, des_path: str=None):
        """
        This function is used to pull the file form the Android file System
        :param src_path: Source path of the file (Inside the Android File system)
        :type src_path: String
        :param des_path: Destination file path where user want to pull the file
        :type des_path: String
        :return: None
        :rtype: None
        """
        try:
            if self.check_device_status():
                try:
                    des_path = des_path if des_path is not None else self.common_keywords.get_adb_pull_file_path()
                    out = subprocess.Popen(f"adb -s {self.device_name} root", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    out = subprocess.Popen(f"adb -s {self.device_name} remount", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    out = subprocess.Popen(f"adb -s {self.device_name} pull {src_path} {des_path}", shell=True,
                                           stdout=subprocess.PIPE).communicate()
                    robot_print_debug(f"Output: {str(out)}")
                    if "1 file pushed" in str(out):
                        return True
                except OSError as os_err:
                    robot_print_error(f"Error to push the file: {src_path} inside : {des_path}, EXCEPTION: {os_err}")
            robot_print_error(f"It seems device: {self.device_name} is offline and RoboFIT not able to push the file",
                              print_in_report=True)
            return False
        except Exception as exp:
            robot_print_error(f"Error to push the file inside the ADB device: {self.device_name}, EXCEPTION: {exp}",
                              print_in_report=True)

    def get_time_from_adb_log(self, suit_name: str, key: str) -> Tuple[Union[str, None], Union[str, None]]:
        """
        This method is used to get the date and time of the given key in ADB logs
        :params: key: Key need to be find in ADB logs
        :return: If key found It will return date and time, otherwise None, None
        :uses:
            date, time = get_time_from_adb_log("MY_KEY")
        """
        try:
            file_path = os.path.join(self.common_keywords.get_logs_screenshot_path(),
                                     "{filename}\{filename}.log".format(
                                         filename=suit_name.split(" ")[0]))
            robot_print_debug(f"Reading {key} for getting timestamp: {file_path}", print_in_report=True)
            with open(file_path, "r", encoding="mbcs") as fp:
                line = fp.readline()
                while line:
                    if key in line:
                        match = re.search("(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).(\d{3})", line)
                        if match:
                            timestamp = match[0]
                            robot_print_info(f"Found timestamp: {timestamp}", print_in_report=True)
                            fp.close()
                            timestamp = timestamp.split(" ")
                            return timestamp[0], timestamp[1]
                    line = fp.readline()
                fp.close()
            return None, None
        except FileNotFoundError as file_err:
            robot_print_error(f"File is not found for getting timestamp from adb logs, EXCEPTION: {file_err}",
                              print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to get the timestamp from the adb logs, EXCEPTION: {exp}")

    def clear_adb_logs(self) -> bool:
        """
        Clear ADB Logs of Device Name Mentioned
        :return: True if Logs Cleared else False
        """
        try:
            if self.check_device_status():
                subprocess.Popen(['adb', '-s', self.device_name, 'logcat', '-b', 'all', '-c'],
                                 stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
                robot_print_debug("Logs cleared", True)
                return True
            else:
                robot_print_error("Logs not cleared due to Device is OFFLINE", True)
                return False
        except Exception as exp:
            robot_print_error(f"Error to clear adb log  s:{exp}")
            return False
