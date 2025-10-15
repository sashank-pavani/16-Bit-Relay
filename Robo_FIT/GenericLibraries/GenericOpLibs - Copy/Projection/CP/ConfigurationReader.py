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
        This is a constructor of Android Auto ConfigurationReader

        If user not provide the global Android Auto configuration file path in the project specific configuration file
        then this ConfigurationReader class read the DEFAULT configuration file form
        'Framework_Components/Projection/CP/cp_config_file.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_list = ""
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, self.common_keyword.team_name,
                                       PROJECT_CONFIG, CP_CONFIG)
            if os.path.isfile(config_path):
                config_path = os.path.join(self.common_keyword.get_root_path(), config_path)
                self.config_list = self.read_configuration(config_path)
            else:
                robot_print_error(f"Please verify configuration file is available for CP", print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ROBO_LIBS,
                                                   ROBO_COMPONENTS, "CP", CP_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except IOError as excp:
            robot_print_error(excp, print_in_report=True)

    def read_configuration(self, path: str) -> Dict:
        """
        return the json in dictionary format
        :param path: path to configuration file
        :return: dictionary form of json file
        """

        with open(path) as json_file:
            try:
                data_dict = json.loads(json_file.read())
                return data_dict
            except json.JSONDecodeError as e:
                robot_print_error("invalid json: %s" % e, print_in_report=True)
                return {}

    def read_int(self, key: str) -> int:
        """
        return int value for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return int(self.config_list[key])
        except KeyError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
            return -1

    def read_string(self, key: str) -> str:
        """
        return string for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
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
            robot_print_error("invalid json value: %s" % e, print_in_report=True)
            return {}
