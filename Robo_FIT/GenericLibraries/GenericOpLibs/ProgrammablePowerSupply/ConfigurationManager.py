from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class ConfiguratorManager:

    def __init__(self):
        self.config = ConfigurationReader()

    def get_device_id(self) -> str:
        try:
            return self.config.read_string('deviceId')
        except Exception as e:
            robot_print_error(f"Error to read the value of device id of PPS, EXCEPTION: {e}")

    def get_baudrate(self) -> int:
        try:
            return self.config.read_int('baudRate')
        except Exception as e:
            robot_print_error(f"Error to read the value of baudrate of PPS, EXCEPTION: {e}")

    def get_device_name(self) -> str:
        try:
            return self.config.read_string('deviceName').upper()
        except Exception as exp:
            robot_print_error(f"Error to get the device name in PPS, EXCEPTION: {exp}")
            
    def get_max_voltage(self):
        try:
            return self.config.read_string("maxVoltage")
        except Exception as exp:
            robot_print_error(f"Error to get the maximum voltage value of PPS, EXCEPTION: {exp}")
    
    def get_max_current(self):
        try:
            return self.config.read_string("maxCurrent")
        except Exception as exp:
            robot_print_error(f"Error to get the maximum current of PPS, EXCEPTION: {exp}")
            
    def get_normal_voltage(self):
        try:
            return self.config.read_string("normalVoltage")
        except Exception as exp:
            robot_print_error(f"Error to get the normal voltage of PPS, EXCEPTION: {exp}")
