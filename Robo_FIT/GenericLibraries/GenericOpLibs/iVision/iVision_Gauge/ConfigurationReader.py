from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os
import json
from typing import Dict, List

class ConfigurationReader:
    """
    This is a JSON reader class for Serial Interface, implemented as a Singleton.
    """

    __instance = None

    @staticmethod
    def get_config_reader() -> 'ConfigurationReader':
        if ConfigurationReader.__instance is None:
            ConfigurationReader()
        return ConfigurationReader.__instance

    def __init__(self):
        """
        Constructor for ConfigurationReader, ensures valid JSON loading.
        """
        if ConfigurationReader.__instance is not None:
            raise Exception(
                f"{__class__} is a Singleton class. Use 'get_config_reader()' to create an instance."
            )
        else:
            ConfigurationReader.__instance = self

        try:
            self.common_keyword = CommonKeywordsClass()
            config_path = os.path.join(
                self.common_keyword.get_root_path(),
                "Robo_FIT",
                "GenericLibraries",
                "GenericOpLibs",
                "iVision",
                "iVision_Gauge",
                "iVision_Gauge_Config_File.json"
            )
            print(f"Loading configuration from: {config_path}")

            # Properly load and debug the JSON structure
            self.config_list = self.read_configuration(config_path)
            print("Parsed Configuration:", json.dumps(self.config_list, indent=4))

            if not self.config_list:
                raise Exception(
                    f"Empty JSON file received. "
                    f"Please check the config file at path: {config_path}"
                )

        except IOError as excep:
            robot_print_error(f"Error reading the configuration file: {excep}", print_in_report=True)

    def read_configuration(self, path: str) -> Dict:
        """Reads a JSON configuration file and returns its contents as a dictionary.
            Returns:
                Dict: Dictionary containing the JSON data, or an empty dictionary if an error occurs.
        """
        try:
            with open(path, 'r') as json_file:
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
        Reads a string value from the JSON configuration based on a dot-separated key path.
        """
        try:
            keys = key.split(".")
            config = self.config_list

            for k in keys:
                print(f"Navigating key: {k}")
                if k not in config:
                    raise KeyError(f"Key '{k}' not found while traversing: {config}")
                config = config[k]

            # Ensure the final value is a string
            if not isinstance(config, str):
                raise ValueError(f"The key '{key}' does not point to a string. Found: {type(config)}")

            print(f"Resolved String: {config}")
            return config

        except KeyError as ke:
            raise KeyError(f"Invalid key in JSON: {ke}")

        except Exception as e:
            raise Exception(f"Error during JSON lookup for key '{key}': {e}")

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

    def read_list(self, key: str) -> list:
        """
        Reads a list value from the JSON configuration based on a dot-separated key path.
        """
        try:
            keys = key.split(".")
            config = self.config_list

            for k in keys:
                print(f"Navigating key: {k}")
                if k not in config:
                    raise KeyError(f"Key '{k}' not found while traversing: {config}")
                config = config[k]

            if not isinstance(config, list):
                raise KeyError(f"The key '{key}' does not point to a list. Found: {type(config)}")

            print(f"Resolved List: {config}")
            return config

        except KeyError as ke:
            raise KeyError(f"Invalid key in JSON: {ke}")

        except Exception as e:
            raise Exception(f"Error during JSON lookup for key '{key}': {e}")

    def read_dict(self, key: str) -> dict:
        """
        Reads a dictionary value from the JSON configuration based on a dot-separated key path.
        """
        try:
            keys = key.split(".")
            config = self.config_list

            for k in keys:
                print(f"Navigating key: {k}")
                if k not in config:
                    raise KeyError(f"Key '{k}' not found while traversing: {config}")
                config = config[k]

            if not isinstance(config, dict):
                raise ValueError(f"The key '{key}' does not point to a dictionary. Found: {type(config)}")

            print(f"Resolved Dictionary: {config}")
            return config

        except KeyError as ke:
            raise KeyError(f"Invalid key in JSON: {ke}")
        except Exception as e:
            raise Exception(f"Error during JSON lookup for key '{key}': {e}")

    def validate_keys(self, required_keys: List[str]):
        """
        Validates the presence of required keys in the configuration.
        :param required_keys: A list of keys that must exist.
        :raises ValueError: If any required key is missing.
        """
        for key in required_keys:
            try:
                self.read_list(key)
            except ValueError as ve:
                print(f"Key Validation Error: {ve}")
                raise ValueError(f"Missing required configuration key: '{key}'")
