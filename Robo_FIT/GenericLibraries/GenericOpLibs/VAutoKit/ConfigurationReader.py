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

    def __init__(self):
        try:
            self.common_keyword = CommonKeywordsClass()
            config_path = os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                  self.common_keyword.team_name,
                                  PROJECT_CONFIG, VAUTOKIT_CONFIG)
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

    def read_string(self, key) -> str:
        try:
            robot_print_debug(f"the key is {key}")
            return str(self.config_list[key])

        except KeyError as e:
            robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
            return ""

    def read_list(self, key: object) -> Dict:
        '''
        return list for respective key
        :param key: key to be searched in dictionary
        :return: corresponding value for the key
        '''
        try:
            return self.config_list[key]
        except KeyError as e:
            robot_print_error(f"Inside Serial invalid json, EXCEPTION {e}", print_in_report=True)
            return {}
