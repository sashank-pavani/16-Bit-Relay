"""
Configuration Reader class with read the configuration file and provide the data.
"""

import os.path
import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ConfigurationReader:
    __instance = None

    @staticmethod
    def get_configuration_reader() -> 'ConfigurationReader':
        f"""
        Static function to create an singleton object of this class.
        :return: ConfigurationReader class Singleton object
        :rtype: object
        """
        if ConfigurationReader.__instance is None:
            ConfigurationReader()
        return ConfigurationReader.__instance

    def __init__(self):
        if ConfigurationReader.__instance is not None:
            raise ClassNotInitializedError(f"{__file__} is a singleton class, so please use "
                                           f"ConfigurationReader.get_configuration_reader() function to create a object.")
        else:
            common_keyword = CommonKeywordsClass()
            config_path = os.path.join(common_keyword.get_root_path(), PROJECT, common_keyword.team_name,
                                       PROJECT_CONFIG,
                                       DOWNLOAD_BUILD_CONFIG_FILE)
            if os.path.isfile(config_path):
                config_path = config_path
            else:
                config_path = os.path.join(os.path.basename(os.path.abspath(__file__)), DOWNLOAD_BUILD_CONFIG_FILE)
            robot_print_info(f"Reading configuration file as : {config_path}")
            self.config = self.read_configuration(config_path)
            ConfigurationReader.__instance = self

    def read_configuration(self, path: str) -> dict:
        """
        return the json in dictionary format
        :param path: path to configuration file
        :return: dictionary form of json file
        """
        with open(path) as json_file:
            try:
                dictionary = json.loads(json_file.read())
                return dictionary
            except json.JSONDecodeError as exp:
                robot_print_error(f"Invalidate json file are provided, path: {path}, EXCEPTION: {exp}",
                                  print_in_report=True)
                return {}

    def read_int(self, key: str) -> int:
        """
        return int value for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return int(self.config[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)

    def read_string(self, key: str) -> str:
        """
        return string for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return str(self.config[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}")

    def read_list(self, key: str) -> dict:
        """
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return self.config[key]
        except ValueError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)


class ClassNotInitializedError(Exception):
    pass
