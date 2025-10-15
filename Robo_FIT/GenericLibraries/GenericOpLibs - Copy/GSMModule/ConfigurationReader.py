import json

from typing import Dict

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os


class ConfiguratorReader:
    """
        Only valid upto second root of json file

    """

    def __init__(self):
        """
        This is a constructor of GSMModule ConfiguratorReader

        If user not provide the global GSMModule configuration file path in the project specific configuration file
        then this ConfigurationReader class read the DEFAULT configuration file form
        '/Framework_Components/GSMModule/gsm_configuration_file.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_list = ""
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, self.common_keyword.team_name,
                                       PROJECT_CONFIG, GSM_CONFIG)
            if os.path.isfile(config_path):
                # config_path = get_suite_path() + config_path
                config_path = os.path.join(self.common_keyword.get_root_path(), config_path)
                self.config_list = self.read_configuration(config_path)
            else:
                robot_print_error(f"Please verify configuration file is available for GSMModule", print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ROBO_LIBS,
                                                   ROBO_COMPONENTS, GSM_MODULE, GSM_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except IOError as exp:
            robot_print_error(exp)

    def read_configuration(self, path: str) -> dict:

        with open(path) as json_file:
            try:
                dict = json.loads(json_file.read())
                return dict
            except json.JSONDecodeError as e:
                robot_print_error("invalid json: %s" % e, print_in_report=True)
                return {}
            except KeyError as e:
                robot_print_error(f"Inside GSM invalid json, EXCEPTION {e}", print_in_report=True)
                return {}

    def read_int(self, key: str) -> int:
        try:
            return int(self.config_list[key])
        except KeyError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
            return -1

    def read_string(self, key: str) -> str:
        try:
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
            return ""

    def read_list(self, key: str) -> Dict:
        try:
            return self.config_list[key]
        except KeyError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
            return {}
