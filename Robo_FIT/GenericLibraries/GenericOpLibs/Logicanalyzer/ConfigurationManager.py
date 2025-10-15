from CRE.Libraries.ProjectLibs.Logicanalyzer.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
import json

class ConfigurationManager:

    def __init__(self):
        self.config = ConfigurationReader()

    def get_device_config(self):
        """
                This method is used to get device configuration from 'logic_config_file'
                :param : None
                :return:enabled_digital_channels , digital_sample_rate , digital_threshold_volts
                """
        try:
            enabled_digital_channels = self.config.read_list("enabled_digital_channels")
            digital_sample_rate = self.config.read_int("digital_sample_rate")
            digital_threshold_volts = self.config.read_string("digital_threshold_volts")

            #return_val = 'enabled_digital_channels =' + enabled_digital_channels + "," + " digital_sample_rate =" + digital_sample_rate + "," + " digital_threshold_volts =" + digital_threshold_volts
            #print(return_val)
            return enabled_digital_channels, digital_sample_rate, digital_threshold_volts
        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_device_id(self):
        """
                        This method is used to get device configuration from 'logic_config_file'
                        :param : None
                        :return:device_id
                        """
        try:
            device_id = self.config.read_string("device_id")
            return device_id

        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_port(self):
        """
                        This method is used to get port from 'logic_config_file'
                        :param : None
                        :return:port
                        """
        try:
            port = self.config.read_int("port")
            return port

        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_serial_one_device(self) -> str:
        try:
            return self.config.read_string("Device")
        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_serial_one_port(self) -> str:
        try:
            return self.config.read_string("COM_Port")
        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_serial_one_ign(self):
        try:
            return self.config.read_string("IGN")
        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

    def get_serial_one_power(self) -> str:
        try:
            return self.config.read_string("Power")
        except json.JSONDecodeError as exp:
            robot_print_error(str(exp), print_in_report=True)

if __name__ == '__main__':
    h = ConfigurationManager()
    a, b, c = h.get_device_config()
    print('Device config =', a, b, c)
    d = h.get_device_id()
    print('Device ID =', d)

