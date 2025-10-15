import json
import os
from typing import Dict, List

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import QFIL_CONFIG, PROJECT, PROJECT_CONFIG, \
    ROBO_FIT, QFIL_DIR
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *


class ConfigurationReader:
    """
        Only valid upto second root of json file
    """

    def __init__(self):
        """
        This is a constructor of ConfiguratorReader.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                            self.common_keyword.team_name, PROJECT_CONFIG,
                                            QFIL_CONFIG)
            robot_print_info(f"QFIL CONFIG_PATH:{self.config_path}")
            if os.path.isfile(self.config_path):
                self.config_list = self.read_configuration(self.config_path)
            else:
                robot_print_error(f"{self.config_path} is not found, "
                                  f"Please place your configuration file inside CRE/<team_name>/ProjectConfiguration",
                                  print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, QFIL_DIR,
                                                   QFIL_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except Exception as excp:
            robot_print_error(f" Error to read the {QFIL_DIR} configuration file, EXCEPTION: {excp}",
                              print_in_report=True)

    def read_configuration(self, path: str) -> Dict:
        """
        return the json in dictionary format
        :param path: path to configuration file
        :type: path: String
        :return: dictionary form of json file
        :rtype: Dict
        """
        with open(path) as json_file:
            try:
                dict = json.loads(json_file.read())
                return dict
            except ValueError as e:
                robot_print_error(f"invalid json: {e}", print_in_report=True)
                return {}

    def read_int(self, key: str) -> int:
        """
        return int value for respective key

        :param key: key to be searched in dictionary
        :type: String
        :return: corresponding value for the key
        :rtype: int
        """
        try:
            return int(self.config_list[key])
        except ValueError as e:
            robot_print_error(f"invalid json value: {e}", print_in_report=True)

    def read_string(self, key: str) -> str:
        """
        return string for respective key

        :param key: key to be searched in dictionary
        :type: key: String
        :return: corresponding value for the key
        :rtype: String
        """
        try:
            return str(self.config_list[key])
        except ValueError as e:
            robot_print_error(f"invalid json value: {e}", print_in_report=True)

    def read_list(self, key: str) -> List:
        """
        return list for respective key
        :param key: key to be searched in dictionary
        :type: Key: String
        :return: corresponding value for the key
        :rtype: List
        """
        try:
            return self.config_list[key]
        except ValueError as e:
            robot_print_error(f"invalid json value: {e}", print_in_report=True)
