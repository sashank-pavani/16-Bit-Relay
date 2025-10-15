import json
from Robo_FIT.GenericLibraries.GenericOpLibs.SystemLogger.ConfigurationReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info


class ConfigurationManager:

    def __init__(self):
        """
        Constructor of ConfiguratioManager
        """
        self.config_file = ConfiguratorReader()

    def get_adb_device_id(self) -> str:
        try:
            return self.config_file.read_string("adbIdUsb")
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_adb_id(self) -> str:
        try:
            return self.config_file.read_string("adbIdNetwork")
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_adb_device_name(self) -> str:
        try:
            return self.config_file.read_string("adbDeviceName")
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_system_logger_status(self) -> bool:
        try:
            value = self.config_file.read_string("enabled")
            if value.lower() == "true":
                return True
            else:
                return False
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_system_log_path(self) -> str:
        try:
            return self.config_file.read_string("systemLogPath")
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_log_type(self) -> str:
        try:
            return self.config_file.read_string("type")
        except ValueError as exp:
            robot_print_error(exp, print_in_report=True)
