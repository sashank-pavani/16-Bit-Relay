import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
import os
from typing import Dict


class ConfiguratorReader:
    """
        Only valid upto second root of json file
    """

    def __init__(self):
        """
        This is a constructor of Performance Utilisation ConfigurationReader
        If user not provide the global Performance Utilisation configuration file path in the project
        specific configuration file then this ConfigurationReader class read the DEFAULT configuration file form
        '<homepath>/PerformanceUtilisation/performance_config_file.json' path.
        :except IOError, if config file not found
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                            self.common_keyword.team_name, PROJECT_CONFIG,
                                            PERFORMANCE_CONFIG)
            if os.path.isfile(self.config_path):
                self.config_list = self.read_configuration(self.config_path)
            else:
                robot_print_error(f"{self.config_path} is not found, "
                                  f"Please place your configuration file inside CRE/<team_name>/ProjectConfiguration",
                                  print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ADB_LOGGER,
                                                   PERFORMANCE_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except Exception as excp:
            robot_print_error(f" Error to read the Adb configuration file, EXCEPTION: {excp}",
                              print_in_report=True)

    def read_configuration(self, path) -> Dict:
        """
        return the json in dictionary format
        :param path: path to configuration file
        :return: dictionary form of json file
        """
        with open(path) as json_file:
            try:
                dict = json.loads(json_file.read())
                return dict
            except json.JSONDecodeError as exp:
                robot_print_error(f"Invalidate json file are provided, path: {path}, EXCEPTION: {exp}",
                                  print_in_report=True)
                return {}

    def read_int(self, key) -> int:
        """
        return int value for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return int(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)

    def read_string(self, key) -> str:
        """
        return string for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)

    def read_list(self, key) -> Dict:
        """
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return self.config_list[key]
        except ValueError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)