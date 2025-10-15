from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.IPps import IPps
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.TenmaPps import TenmaPps
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.ConfigurationManager import ConfiguratorManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import TENAM_PPS


class PpsClass(IPps):
    """This Class internally call Tenma 72-2710 programmable power supply command based on Tenma Manual Guide"""

    def __init__(self):
        """
        This Constructor creates object which are required for this file.
        """
        self.current_pps = None
        self.config_manager = ConfiguratorManager()
        self.__initialize_power_supply()
        self.maxVoltage = self.config_manager.get_max_voltage()
        self.normalVoltage = self.config_manager.get_normal_voltage()

    def __initialize_power_supply(self):
        """
        This is Tenma PPS class Constructor which is used for creating an instance of PPS device by providing
        baud-rate of "9600" and port = Event ID from device manager or Comport number from device manager and 2second
        timeout
        """
        device_name = self.config_manager.get_device_name()
        robot_print_debug(f"Initializing PPS for device: {device_name}")
        if device_name == TENAM_PPS:
            self.current_pps = TenmaPps.get_pps_instance()
        else:
            robot_print_error(text=f"Error to initialize the PPS,"
                                   f"\nPlease check the configuration file and provide valid PPS name inside "
                                   f"key 'deviceName'", print_in_report=True, underline=True)
            raise AttributeError("Error to initialize the PPS, Wrong attribute pass in configuration file.")

    def perform_pps_on(self):
        """
        This Function Perform PPS ON by setting nominal voltage.
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        self.current_pps.perform_pps_on()

    def perform_pps_off(self):
        """
        TODO:This Function needs to Fix, If we set cutoff it shows voltage "03.00" and current:"01.21"
        This Function Perform PPS OFF by cutting off PPS Voltage.
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        self.current_pps.perform_pps_off()

    def initialize_pps(self):
        """
        This Function Initialize PPS
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        self.current_pps.initialize_pps()

    def set_output_voltage(self, voltage_value: str):
        """
        This Function Set output Voltage user provide in current_value parameter
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        self.current_pps.set_output_voltage(voltage_value=voltage_value)

    def get_voltage_value(self):
        """
        This Function Get output Voltage.
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        return self.current_pps.get_voltage_value()

    def set_output_current(self, current_value):
        """
        This Function Set output Current user provide in current_value parameter
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        self.current_pps.set_output_current(current_value=current_value)

    def get_current_value(self):
        """
        This Function returns current value.
        :return :None
        """
        if self.current_pps is None:
            raise TypeError("PPS is not initialize, the object is none. Please check the logs")
        return self.current_pps.get_current_value()
