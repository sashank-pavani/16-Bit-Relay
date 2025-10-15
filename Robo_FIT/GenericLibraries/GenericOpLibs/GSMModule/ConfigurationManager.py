from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.ConfigurationReader import ConfiguratorReader
import re
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class ConfigurationManager:
    """
    This class is used to manage all the values from configuration file differently
    it gives all the values from the configuration file
    """

    def __init__(self):
        """
        Constructor of ConfigurationManager
        :param config_path: global path of configuration file
        """
        self.config_file = ConfiguratorReader()

    def read_recipient_number(self):
        pattern = re.compile(r'^(?:\+?91)?[0-9]\d{9,13}$')
        recipient_number = self.config_file.read_string("recipient_no")
        try:
            if pattern.match(recipient_number):
                return recipient_number
        except ValueError as e:
            print("Recipient number is not in the valid format")

    def read_message(self) -> str:
        return self.config_file.read_string("message")

    def read_gsm_device_id(self, device_num: str) -> str:
        try:
            device_info = self.config_file.read_list("deviceInfo")
            for devices in device_info:
                if str(devices["deviceNumber"]).upper() == device_num.upper():
                    return devices["deviceId"]
        except KeyError as key_error:
            robot_print_error(f"Error to read the GSM module id for device {device_num}, EXCEPTION: {key_error}")

    def gsm_read_device_name(self) -> str:
        try:
            return self.config_file.read_string("deviceName")
        except KeyError as exp:
            robot_print_error(f"Error to get the device name for the GSM configuration file. EXCEPTION: {exp}")

    def read_mode(self) -> str:
        return self.config_file.read_string("mode")

    def read_baudrate(self) -> int:
        return self.config_file.read_int("baudrate")
