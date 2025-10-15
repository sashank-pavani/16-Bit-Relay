import os
import json
import pandas as pd
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ConfiguratorReader:
    """
        This Class use for make Nested JSON Flatten using read_flatten_json function and then pass key
        accordingly to read it's value.
    """

    def __init__(self):
        """
        This is a constructor of HandleBarControl ConfigurationReader

        If user not provide the global ADB logger configuration file path in the project specific configuration file
        then this ConfigurationReader class read the DEFAULT configuration file form
        'Robo_FIT/GenericLibraries/GenericOpLibs/HandleBarControl/handlebar_key_code_config.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            self.config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                            self.common_keyword.team_name, PROJECT_CONFIG,
                                            HANDLE_BAR_CONTROL_CONFIG_FILE)
            robot_print_info(f"ConfigPath:{self.config_path}")
            if os.path.isfile(self.config_path):
                self.config_list = self.read_configuration(self.config_path)
            else:
                robot_print_error(f"{self.config_path} is not found, "
                                  f"Please place your configuration file inside CRE/ProjectConfiguration",
                                  print_in_report=True)
                default_config_path = os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, HANDLE_BAR_CONTROL,
                                                   HANDLE_BAR_CONTROL_CONFIG_FILE)
                self.config_list = self.read_configuration(default_config_path)
        except Exception as excp:
            robot_print_error(f" Error to read the HandleBarControl configuration file, EXCEPTION: {excp}",
                              print_in_report=True)

    def read_configuration(self, path) -> dict:
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

    def read_flatten_json(self):
        """
        This Deeply nested JSON and make it flatten please check example given below for more clear idea.
        :return: return flatten json by making nested keys appended till value and assign value to it accordingly.
                example: {'a':'1',{'b': '2',{'c':'3'}}}
                        result {'a': '1','a_b':'2','a_b_c':'3'}
        """
        df = pd.json_normalize(dict(self.config_list.items()), sep='_')
        return df.to_dict(orient='records')[0]

    def read_int(self, key) -> int:
        """
        return int value for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            dictionary = self.read_flatten_json()
            return int(dictionary[key])
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
            dictionary = self.read_flatten_json()
            return str(dictionary[key])
        except KeyError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)

    def read_list(self, key) -> dict:
        """
        This function used to read value one level from root only
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return self.config_list[key]
        except ValueError as e:
            robot_print_error(f"Try to read invalidate key from the JSON file, EXCEPTION: {e}",
                              print_in_report=True)
