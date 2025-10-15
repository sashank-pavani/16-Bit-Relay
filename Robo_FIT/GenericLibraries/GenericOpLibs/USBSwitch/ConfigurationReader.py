import json
import os
from typing import Dict

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *


class ConfigurationReader:
    """Only valid upto second root of json file"""

    def __init__(self):
        """
        This is a constructor of USB Controller ConfiguratorReader
        If user not provide the global USB Controller configuration file path in the project specific configuration file
        then this ConfigurationReader class read the DEFAULT configuration file form
        '/Framework_Components/USBSwitch/usb_switch_config_file.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, self.common_keyword.team_name,
                                       PROJECT_CONFIG, USB_CONFIG)
            robot_print_info(f"USB JSON path : {config_path}")

            if os.path.isfile(config_path):
                self.config_list = self.read_configuration(config_path)
                robot_print_info(f"USB JSON path : {config_path}, data: {self.config_list}")
            else:
                robot_print_error(f"Please verify configuration file is available for USBSwitch",
                                  print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ROBO_LIBS,
                                                   ROBO_COMPONENTS, USB_SWITCH_MODULE, USB_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
                robot_print_info(f"USB JSON path : {config_path}, data: {self.config_list}")
        except IOError as exp:
            robot_print_error(exp)

    """Load the json file"""

    def read_configuration(self, path: str) -> Dict:
        with open(path) as json_file:
            try:
                data_dict = json.loads(json_file.read())
                return data_dict
            except json.JSONDecodeError as e:
                robot_print_error("invalid json: %s" % e, print_in_report=True)
                return {}

    def read_int(self, key: str) -> int:
        try:
            return int(self.config_list[key])
        except ValueError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)

    def read_string(self, key: str) -> str:
        try:
            return str(self.config_list[key])
        except ValueError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)

    def read_list(self, key: str) -> list:
        try:
            return self.config_list[key]
        except ValueError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
