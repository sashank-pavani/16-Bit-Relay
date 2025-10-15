import json
from typing import Dict
from Robo_FIT.GenericLibraries.GenericOpLibs.ADBLogger.ConfigurationReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ConfigurationManager:

    def __init__(self):
        """
        Constructor of ConfiguratioManager
        """
        self.config_file = ConfiguratorReader()
        self.common_keyword = CommonKeywordsClass()

    def get_adb_usb_id(self) -> str:
        return self.config_file.read_string("adbIdUsb")

    def get_adb_network_id(self) -> str:
        return self.config_file.read_string("adbIdNetwork")

    def get_adb_device_name(self) -> str:
        return self.config_file.read_string("adbDeviceName")

    def get_path(self) -> str:
        return self.config_file.read_string(self.common_keyword.get_report_path())

    def get_enabled_status(self) -> bool:
        try:
            value = self.config_file.read_string("enabled")
            if value.lower() == "true":
                return True
            else:
                return False
        except json.JSONDecodeError as exp:
            print(exp)
            return False

    def get_logger(self) -> Dict:
        return self.config_file.read_list("logger")

    def get_by_type(self, logger_type) -> str:
        logger_list = self.get_logger()
        return logger_list[str(logger_type.lower())]

    def get_type_verbose(self) -> str:
        return self.get_by_type("verbose")

    def get_type_debug(self) -> str:
        return self.get_by_type("debug")

    def get_type_error(self) -> str:
        return self.get_by_type("error")

    def get_type_info(self) -> str:
        return self.get_by_type("info")

    def get_type_fatal(self) -> str:
        return self.get_by_type("fatal")

    def get_type_warning(self) -> str:
        return self.get_by_type("warning")

    def get_type_silent(self) -> str:
        return self.get_by_type("silent")

    def get_log_type(self) -> str:
        return self.config_file.read_string("type")
