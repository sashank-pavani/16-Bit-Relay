import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os
from typing import Dict, List


class ConfigurationReader:
    """
        Only valid upto second root of json file

    """

    def __init__(self):
        """
        This is a constructor of Relay ConfiguratorReader
        If user not provide the global Relay configuration file path in the project specific configuration file
        then this ConfigurationReader class read the DEFAULT configuration file form
        '/Framework_Components/Relay/relay_config_file.json' path.
        """
        try:
            self.common_keyword = CommonKeywordsClass()
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                       self.common_keyword.team_name,
                                       PROJECT_CONFIG, RELAY_CONFIG)
            self.config_list = self.read_configuration(config_path)
            if not bool(self.config_list):
                raise Exception(f"Empty Realy json file received, "
                                f"\nPlease check the relay_config_file.json in side path: {config_path}")
        except IOError as excep:
            robot_print_error(f"Error to read the Relay configuration file, EXCEPTION: {excep}", print_in_report=True)

    def read_configuration(self, path) -> Dict:
        """
        return the json in dictionary format
        :param path: path to configuration file
        :return: dictionary form of json file
        """
        with open(path) as json_file:
            try:
                data_dict = json.loads(json_file.read())
                return data_dict
            except json.JSONDecodeError as exp:
                robot_print_error(f"Inside relay invalid json, EXCEPTION {exp}", print_in_report=True)
            except KeyError as e:
                robot_print_error(f"Inside relay invalid json, EXCEPTION {e}", print_in_report=True)
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
            robot_print_error(f"Inside relay, trying to read invalidate key, EXCEPTION {e}", print_in_report=True)
            return -1

    def read_string(self, key) -> str:
        """
        return string for respective key

        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return str(self.config_list[key])
        except KeyError as e:
            robot_print_error(f"Inside relay, trying to read invalidate key, EXCEPTION {e}", print_in_report=True)
            return ""

    def read_list(self, key) -> List:
        """
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        """
        try:
            return self.config_list[key]
        except KeyError as e:
            robot_print_error(f"Inside relay, trying to read invalidate key, EXCEPTION: {e}", print_in_report=True)
            return []
