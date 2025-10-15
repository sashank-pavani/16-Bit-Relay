import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os
from typing import Dict, List

class ConfigurationReader:
    """
    This is a josn reader class for Serial Interface
    """


    __instance = None

    @staticmethod
    def get_config_reader() -> 'ConfigurationReader':
        if ConfigurationReader.__instance is None:
            ConfigurationReader()
        return ConfigurationReader.__instance

    def __init__(self):
        if ConfigurationReader.__instance is not None:
            raise Exception(
                f"{__class__} is a Singleton class, to create a object of this please use get_config_reader()")
        else:
            ConfigurationReader.__instance = self
            try:
                self.common_keyword = CommonKeywordsClass()
                config_path = os.path.join(self.common_keyword.get_root_path(), "Robo_FIT",
                                           "GenericLibraries","GenericOpLibs","cVision","cVisionImage", "cVisionImage_Config_File.json")
                j=open(config_path)
                data = json.load(j)
                self.config_list = self.read_configuration(config_path)
                if not bool(self.config_list):
                    raise Exception(f"Empty Realy json file received, "
                                f"\nPlease check the relay_config_file.json in side path: {config_path}")

            except IOError as excep:
                robot_print_error(f"Error to read the Relay configuration file, EXCEPTION: {excep}", print_in_report=True)

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

    def read_string(self, key: str) -> str:
        """
        Reads a string value from the configuration, supporting nested keys in dot notation.
        :param key: The key to read from the configuration (e.g., "paths.reference_image").
        :return: The corresponding string value or an empty string if not found.
        """
        try:
            robot_print_debug(f"The key is {key}")
            keys = key.split('.')  # Split the key to support nested structure
            value = self.config_list
            for k in keys:
                value = value[k]  # Traverse through nested dictionary
            return str(value)
        except KeyError as e:
            robot_print_error(f"Invalid key in JSON, EXCEPTION {e}", print_in_report=True)
            return ""

    def read_list(self, key: str) -> List[int]:
        """
        Reads a list value from the configuration, supporting nested keys in dot notation.
        :param key: The key to read from the configuration (e.g., "ref_img_curved_bar.fg_color").
        :return: The corresponding list value or an empty list if not found.
        """
        try:
            keys = key.split('.')  # Split the key to support nested structure
            value = self.config_list
            for k in keys:
                value = value[k]  # Traverse through nested dictionary
            if isinstance(value, list):
                return value
            else:
                robot_print_error(f"Expected a list for key '{key}', but got {type(value).__name__}.",
                                  print_in_report=True)
                return []
        except KeyError as e:
            robot_print_error(f"Invalid key in JSON for list, EXCEPTION {e}", print_in_report=True)
            return []
