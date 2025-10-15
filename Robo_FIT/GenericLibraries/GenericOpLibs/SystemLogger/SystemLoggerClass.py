import re
import time
import subprocess
from Robo_FIT.GenericLibraries.GenericOpLibs.SystemLogger.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
import os


class SystemLoggerClass:
    _DEVICE = ""
    _ENABLED = ""

    def __init__(self):
        """
        Constructor of SystemLoggerClass
        """
        self.config_manager = ConfigurationManager()
        self.system_log_path = self.config_manager.get_system_log_path()

        if SystemLoggerClass._ENABLED == "":
            SystemLoggerClass._ENABLED = self.config_manager.get_system_logger_status()
        self.enabled = SystemLoggerClass._ENABLED
        self.helper = CommonKeywordsClass()

        if SystemLoggerClass._DEVICE == "":
            SystemLoggerClass._DEVICE = self.__get_device()

        self.device = SystemLoggerClass._DEVICE

    def __get_device(self) -> str:
        """
        get device name according to adb usb id or network id provided in configuration file
        :return: device name
        """
        network_id = self.config_manager.get_adb_id()
        usb_id = self.config_manager.get_adb_device_id()

        device_list = self._get_devices_list()
        if network_id != "":
            if network_id in device_list:
                return network_id
        if usb_id != "":
            if usb_id in device_list:
                return usb_id
        else:
            robot_print_error("Please mention adb Device Id and Network Id in system configuration file")
            print("Please mention adb Device Id and Network Id in system configuration file")
            return ""

    def __pull_adb_logs(self, file_path: str):
        """
        Pull adb logs from System
        :param file_path:
        :return:
        """
        try:

            if self.device is not None:
                subprocess.call(['adb', '-s', self.device, 'root'], stderr=subprocess.PIPE)
                time.sleep(5)
                subprocess.call(['adb', '-s', self.device, 'remount'], stderr=subprocess.PIPE)
                subprocess.call(['adb', '-s', self.device, 'pull',
                                 self.config_manager.get_system_log_path(), file_path], stderr=subprocess.PIPE)
        except Exception as ex:
            robot_print_error(" Error while pulling logs from system due to error %s" % ex, print_in_report=True)

    def __create_logger_directory(self, file_path: str):
        """
        Create Folder hirerchy
        :param file_path: suitename or testcase name
        :return: None
        """

        if os.path.isdir(file_path):
            robot_print_error("Directory at path: %s already exist" % file_path)
        else:
            os.makedirs(file_path, mode=0o777)
            robot_print_info("Directory Created at path: %s" % file_path, print_in_report=True)

    def __set_log_type(self) -> bool:
        '''
        set type according to which logs should be saved
        :return:
        '''
        log_type = self.config_manager.get_log_type()
        if log_type.upper() == "ALLLOGS":
            return True
        elif log_type.upper() == "TESTCASEWISE":
            return False
        else:
            robot_print_error("Invalid type value. Please mention ALLLOGS or TESTCASEWISE", print_in_report=True)

    def get_suite_system_logs(self, suitename: str):
        """
        Store system logs suite wise
        set type value "ALLLOGS" in configuration file
        :return: None
        """
        if self.enabled:
            log_type = self.__set_log_type()
            if log_type:
                path = self.helper.create_system_log_directory()
                suite_id = suitename.split(".")[-1]
                file_path = os.path.join(path, suite_id)
                self.__create_logger_directory(file_path)
                self.__pull_adb_logs(file_path=file_path)

    def get_testcase_system_logs(self, testcase: str):
        """
        Store system logs suite wise
        set type value "TESTCASEWISE" in configuration file
        :return:
        """
        if self.enabled:
            type = self.__set_log_type()
            if not type:
                path = self.helper.create_system_log_directory()
                test_id = testcase.split(" ")[0]
                file_path = os.path.join(path, test_id)
                self.__create_logger_directory(file_path)
                self.__pull_adb_logs(file_path=file_path)

    def _get_devices_list(self, adb_path: str = 'adb'):
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call([adb_path, 'start-server'], stdout=devnull,
                                  stderr=devnull)
        out = self._split_lines(
            subprocess.check_output([adb_path, 'devices']).decode('utf-8'))
        # The first line of `adb devices` just says "List of attached devices", so
        # skip that.
        devices = []
        for line in out[1:]:
            if not line.strip():
                continue
            if 'offline' in line:
                continue
            serial, _ = re.split(r'\s+', line, maxsplit=1)
            devices.append(serial)
        return devices

    def _split_lines(self, s: str):
        """Splits lines in a way that works even on Windows and old devices.
        Windows will see \r\n instead of \n, old devices do the same, old devices
        on Windows will see \r\r\n.
        """

        return re.split(r'[\r\n]+', s.rstrip())
