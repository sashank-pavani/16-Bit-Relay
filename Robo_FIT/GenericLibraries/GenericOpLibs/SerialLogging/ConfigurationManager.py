from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
import json


class ConfigurationManager:

    def __init__(self):
        self.config_reader = ConfigurationReader()

    def get_serial_one_name(self) -> str:
        try:
            serial_one = self.config_reader.read_list("serialOne")
            return serial_one["name"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_one_port(self) -> str:
        try:
            serial_one = self.config_reader.read_list("serialOne")
            return serial_one["id"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_one_baudrate(self):
        try:
            serial_one = self.config_reader.read_list("serialOne")
            return serial_one["baudrate"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_two_name(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialTwo")
            return serial_two["name"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_two_port(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialTwo")
            return serial_two["id"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_two_baudrate(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialTwo")
            return serial_two["baudrate"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_three_name(self) -> str:
        try:
            serial_one = self.config_reader.read_list("serialThree")
            return serial_one["name"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_three_port(self) -> str:
        try:
            serial_one = self.config_reader.read_list("serialThree")
            return serial_one["id"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_three_baudrate(self) -> str:
        try:
            serial_one = self.config_reader.read_list("serialThree")
            return serial_one["baudrate"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_four_name(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialFour")
            return serial_two["name"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_four_port(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialFour")
            return serial_two["id"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)

    def get_serial_four_baudrate(self) -> str:
        try:
            serial_two = self.config_reader.read_list("serialFour")
            return serial_two["baudrate"]
        except json.JSONDecodeError as exp:
            robot_print_error(exp, print_in_report=True)
