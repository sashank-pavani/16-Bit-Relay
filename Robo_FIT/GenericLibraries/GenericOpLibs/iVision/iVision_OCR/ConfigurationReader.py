from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os
import json
from typing import Dict, List

class ConfigurationReader:
    """
    This is a JSON Reader class for Serial Interface, implemented as a Singleton.
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
                f"{__class__} is a Singleton class. Use 'get_config_reader()' to create an instance."
            )
        else:
            ConfigurationReader.__instance = self

        try:
            self.common_keyword = CommonKeywordsClass()  # Ensure this class is correctly implemented

            config_path = os.path.join(
                self.common_keyword.get_root_path(),
                "Robo_FIT",
                "GenericLibraries",
                "GenericOpLibs",
                "iVision",
                "iVision_OCR",
                "iVision_OCR_Config_File.json"
            )

            self.config_list = self.read_configuration(config_path)

            if not self.config_list:
                raise Exception(
                    f"Empty JSON file received. "
                    f"Please check the config file at path: {config_path}"
                )

        except IOError as excep:
            robot_print_error(f"Error reading the configuration file: {excep}", print_in_report=True)

    def read_configuration(self, path: str) -> Dict:
        """
        Reads the JSON configuration file with support for multilingual text.
        """
        try:
            with open(path, 'r', encoding='utf-8') as json_file:  # Use 'utf-8' for multilingual support
                dict_data = json.load(json_file)
                print("Loaded configuration:", dict_data)  # Debug output
                return dict_data
        except json.JSONDecodeError as exp:
            robot_print_error(f"Invalid JSON format in file, EXCEPTION: {exp}", print_in_report=True)
            return {}
        except IOError as excep:
            robot_print_error(f"Error reading the configuration file: {excep}", print_in_report=True)
            return {}
        except Exception as e:
            robot_print_error(f"Unexpected exception when reading configuration, EXCEPTION: {e}", print_in_report=True)
            return {}

    def read_string(self, key: str) -> str:
        """
        Reads a string value from the configuration using a nested key.

        :param key: The nested key (e.g., "api_urls.detect_telltale.url").
        :return: The corresponding string value or raises an exception if not found.
        """
        try:
            robot_print_debug(f"The key is: {key}")
            keys = key.split(".")
            value = self.config_list
            for k in keys:
                value = value[k]  # Traverse the nested dictionary
            return str(value)
        except KeyError as e:
            robot_print_error(f"Invalid key in JSON, EXCEPTION: {e}", print_in_report=True)
            raise ValueError(f"Key '{key}' not found in configuration file.")

    def read_list(self, key: str) -> List:
        """
        Reads a list value from the configuration.

        :param key: The key to look up.
        :return: List of values or an empty list if not found.
        """
        try:
            return self.config_list[key]
        except KeyError as e:
            robot_print_error(f"Invalid key in JSON, EXCEPTION: {e}", print_in_report=True)
            return []

    def read_int(self, key: str) -> int:

        """
        Reads an integer from the configuration.

        :param key: The key to look up.
        :return: Integer value or -1 if the key is not found.
        """
        try:
            return int(self.read_string(key))
        except ValueError:
            robot_print_error(f"Invalid integer format for key '{key}'", print_in_report=True)
            return -1

    def validate_keys(self, required_keys: List[str]):
        """
        Validates the presence of required keys in the configuration.

        :param required_keys: List of keys that must exist in the JSON file.
        """
        for key in required_keys:
            try:
                self.read_string(key)
            except ValueError:
                raise ValueError(f"Missing required configuration key: '{key}'")
