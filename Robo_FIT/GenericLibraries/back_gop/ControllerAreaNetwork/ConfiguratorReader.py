import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
import os


class ConfiguratorReader:
    """
        Only valid upto second root of json file

    """

    def __init__(self):
        """
        This is a constructor of ControllerAreaNetwork ConfigurationReader

        If user not provide the global ControllerAreaNetwork configuration file path in the project specific
        configuration file then this ConfigurationReader class read the DEFAULT configuration file form
        'Robo_FIT/GenericLibraries/GenericOpLibs/ControllerAreaNetwork/can_config_file.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_path = self.common_keyword.get_path(CAN_CONFIG, parent=PROJECT_CONFIG, is_file=True,
                                                            is_dir=False)
            robot_print_info(f"CONFIG_PATH:{self.config_path}")
            if os.path.isfile(self.config_path):
                self.config_list = self.read_configuration(self.config_path)
            else:
                robot_print_error(f"{self.config_path} is not found, "
                                  f"Please place your configuration file inside CRE/ProjectConfiguration",
                                  print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, CAN_DIR,
                                                   CAN_CONFIG)
                self.config_list = self.read_configuration(default_config_path)
        except Exception as exp:
            robot_print_error(f" Error to read the ControllerAreaNetwork configuration file, EXCEPTION: {exp}",
                              print_in_report=True)

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
            return int(self.config_list[key])
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
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}")

    def read_list(self, key: str) -> dict:
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
