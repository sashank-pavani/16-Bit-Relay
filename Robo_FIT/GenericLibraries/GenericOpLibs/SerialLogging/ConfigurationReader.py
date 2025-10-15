import json
import os
from typing import Dict

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *


class ConfigurationReader:
    """
    This is a josn reader class for Serial Interface
    """

    def __init__(self):
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_list = ""
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, self.common_keyword.team_name,
                                       PROJECT_CONFIG, SERIAL_CONFIG)
            if os.path.isfile(config_path):
                # config_path = get_suite_path() + config_path
                config_path = os.path.join(self.common_keyword.get_root_path(), config_path)
                self.config_list = self.read_configuration(config_path)
            else:
                robot_print_error(f"Please verify configuration file is available for SerialLogger")
                print("Please verify configuration file is available for SerialLogger")
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ROBO_LIBS,
                                                   ROBO_COMPONENTS, SERIAL_MODULE, SERIAL_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except IOError as exp:
            robot_print_error(exp, print_in_report=True)

    def read_configuration(self, path: str) -> Dict:
        with open(path) as json_file:
            try:
                dict_data = json.loads(json_file.read())
                json_file.close()
                return dict_data
            except json.JSONDecodeError as exp:
                robot_print_error(f"Inside Serial invalid json, EXCEPTION {exp}", print_in_report=True)
            except KeyError as e:
                robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
                return {}

    def read_int(self, key) -> int:
        try:
            return int(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
            return -1

    def read_string(self, key) -> str:
        try:
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
            return ""

    def read_list(self, key) -> Dict:
        '''
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        '''
        try:
            return self.config_list[key]
        except KeyError as e:
            robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
            return {}
