#!/usr/bin/env python
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.ConfigurationManager import ConfiguratorManager
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.IPps import IPps
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug, robot_print_error
from serial import Serial
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.serial_interface import _get_device_from_script
import re


class TenmaPps(Serial, IPps):
    """ Class exposing interface to Tenma 72-2710 programmable power supply."""

    __instance = None
    CURRENT_REGEX = re.compile(r"[0-4]\.\d{3}|5\.000")  # Allowing not more than 5.000A
    VOLTAGE_REGEX = re.compile(r"[0-1]\d\.\d{2}|30\.00")  # Allowing not more than 20.00V

    @staticmethod
    def get_pps_instance() -> 'TenmaPps':
        """
        This Method Creates Single Tone Class of PPS Device.
        """
        if TenmaPps.__instance is None:
            TenmaPps()
        return TenmaPps.__instance

    def __init__(self):
        """
        This is Tenma PPS class Constructor which is used for creating an instance of PPS device by providing
        baud-rate of "9600" and port = Event ID from device manager or Comport number from device manager and 2second
        timeout
        """
        if TenmaPps.__instance is not None:
            raise Exception("This is a PPS class ")
        else:
            self.config_manager = ConfiguratorManager()
            path = _get_device_from_script(self.config_manager.get_device_id())
            baudrate = self.config_manager.get_baudrate()
            super(self.__class__, self).__init__(port=path,
                                                 baudrate=baudrate,
                                                 timeout=2)
            TenmaPps.__instance = self
        self.path = self.config_manager.get_device_id()

    def perform_pps_on(self):
        """
        This Function Perform PPS ON by setting nominal voltage.
        :return :None
        """
        self.set_output_voltage(self.config_manager.get_normal_voltage())

    def perform_pps_off(self):
        """
        TODO:This Function needs to Fix, If we set cutoff it shows voltage "03.00" and current:"01.21"
        This Function Perform PPS OFF by cutting off PPS Voltage.
        :return :None
        """
        self.cut_off_supply()

    def initialize_pps(self):
        """
        This Function Initialize PPS
        :return :None
        """
        if self.isOpen():
            robot_print_debug("Initializing programmable power supply for complete test.\n", True)
            robot_print_debug("Fetching power supply info...")
            ret = self.write("*IDN?".encode())
            sleep(0.1)
            assert ret == 5, "Error writing *IDN? to Tenma PPS"
            robot_print_debug(f"{self.read(1024)}")
            self.cut_off_supply()
            robot_print_debug("Turning on over current protection...")
            ret = self.write("OCP1".encode())
            sleep(0.1)
            assert ret == 4, "Error writing OCP1 to Tenma PPS"
            normal_voltage = self.config_manager.get_normal_voltage()
            match = re.search(r"\d\d.\d\d", normal_voltage)
            if match:
                self.set_output_current("3.000")
                self.set_output_voltage("12.00")
                self.connect_supply()
            else:
                robot_print_error(f"It seems you provide wrong value in configuration file for 'normalVoltage', "
                                  f"Please check the configuration file and provide in XX.XX format")
        else:
            raise AssertionError("Port %s is closed." % self.path)

    def set_output_current(self, current_value: str):
        """
        This Function Set output Current user provide in current_value parameter
        :return :None
        """
        if not TenmaPps.CURRENT_REGEX.match(current_value):
            raise ValueError("Current value should be between 0.00A to 5.00A")
        robot_print_debug("Setting output current to %sA." % current_value, True)
        self.write(("ISET1:" + current_value).encode())
        sleep(0.1)
        self.write("ISET1?".encode())
        sleep(0.1)
        if self.read(1024) != current_value.encode():
            raise Exception("Could not set output current.")

    def get_voltage_value(self):
        """
        This Function Get output Voltage.
        :return :None
        """
        robot_print_debug("Getting voltage consumption...")
        self.write("VSET1?".encode())
        sleep(0.1)
        # return float(self.read(1024).decode("utf-8"))
        return self.read(1024)

    def set_output_voltage(self, voltage_value: str):
        """
        This Function Set output Voltage as user provide in voltage_value.
        :return :None
        """
        if not TenmaPps.VOLTAGE_REGEX.match(voltage_value):
            raise ValueError("Voltage value should be between 0.00V to 30.00V")
        robot_print_debug("Setting output voltage to %sV" % voltage_value, print_in_report=True)
        self.write(("VSET1:" + voltage_value).encode())
        sleep(0.1)
        self.write("VSET1?".encode())
        sleep(0.1)
        # robot_print_debug(f"voltage_value.encode()--{voltage_value}",print_in_report=True)
        # robot_print_debug(f"self.read(1024)--{self.read(1024)}",print_in_report=True)
        # value = (str(self.read(1024)) + str("V"))
        # robot_print_debug(f"Value--{value}")
        # robot_print_debug(f"voltage_value.encode()--{voltage_value.encode()}")
        # if (str(self.read(1024)) + str("V")) != str(voltage_value.encode()):
        #     raise Exception("Could not set output voltage.")

    def cut_off_supply(self):
        """
        TODO:This Function needs to Fix, If we set cutoff it shows voltage "03.00" and current:"01.21"
        This Function Cut off the Power Supply.
        :return :None
        """
        robot_print_debug("Cutting off power supply output...", True)
        ret = self.write("OUT0".encode())
        sleep(0.1)
        assert ret == 4, "Error writing OUT0 to Tenma PPS"

    def connect_supply(self):
        """
        This Function Connect Power Supply If it Disconnected Previously.
        :return :None
        """
        robot_print_debug("Connecting power supply output...", True)
        ret = self.write("OUT1".encode())
        sleep(1)
        assert ret == 4, "Error writing OUT1 to Tenma PPS"

    def close(self):
        """
        This Function Close the connection with pps.
        :return :None
        """
        robot_print_debug("Closing connection to power supply...", True)
        super(self.__class__, self).close()

    def get_current_value(self):
        """
        This Function returns current value.
        :return :None
        """
        robot_print_debug("Getting the value of output current set...", True)
        self.write("IOUT1?".encode())
        sleep(0.1)
        return float(self.read(1024).decode("utf-8"))
