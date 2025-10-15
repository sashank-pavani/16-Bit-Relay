from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
import json
import os


class ConfigurationManager:
    """
    This class is for CAN->to manage configuration
    """

    def __init__(self):
        self.config = ConfigurationReader()
        self.common_keyword = CommonKeywordsClass()

    def get_serial_device(self) -> str:
        """
            This method is used to read the Device from configuration file
            :return: Device
        """
        try:
            return self.config.read_string("device")
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_port(self) -> str:
        """
        This method is used to read the port from configuration file
        :return: COM_Port
        """
        try:
            return self.config.read_string("comPort")
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_relay_no(self, relay: str):
        relay_list = self.config.read_list("relay")
        for data in relay_list:
            if relay.lower() == data["relayName"]:
                return data["pinNumber"]
        raise ValueError("It seems port number and device name not provide in configuration file of Relay.")

    def get_speed(self):
        """
        This method is used to read the can speed from configuration file
        :return: speed
        """
        try:
            return self.config.read_string("canSpeed")
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_vautocan_trace_file_name(self) -> str:
        """
        This method is used to read logger file path from the configuration file
        :return: CAN logger file path as String
        """
        try:
            return self.config.read_string("vautocanTraceFileName")
        except TypeError:
            robot_print_error("'canTraceFileName' Key not present in can_config_file.json")

    def get_vautocan_trace_file_path(self, file_name: str) -> str:
        """
                This method is used to read the can trace file name  from configuration file
                :return: path of the trace directory
        """
        try:
            return os.path.join(self.common_keyword .get_vautocan_trace_dir(), file_name)
        except TypeError:
            robot_print_error("'canTraceFileName' Key not present in can_config_file.json")
