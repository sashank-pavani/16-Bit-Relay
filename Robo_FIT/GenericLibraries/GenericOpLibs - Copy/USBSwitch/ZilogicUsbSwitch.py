#!/usr/bin/env python
from serial import Serial, SerialException
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.IUsbSwitch import IUsbSwitch
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.serial_interface import _get_device_from_script
import re


class ZilogicUsbSwitch(Serial, IUsbSwitch):
    __instance = None
    """ Class exposing interface to Zilogic USB Switch."""

    @staticmethod
    def get_serial_instance():
        """Staic Method"""
        if ZilogicUsbSwitch.__instance is None:
            ZilogicUsbSwitch()
        return ZilogicUsbSwitch.__instance

    """init define with path and baudRate"""

    def __init__(self):
        if ZilogicUsbSwitch.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.config_manager = ConfigurationManager()
            self.path = _get_device_from_script(self.config_manager.get_device_id())
            super(self.__class__, self).__init__(port=self.path, baudrate=self.config_manager.get_baudrate(),write_timeout=5,timeout=5)
            ZilogicUsbSwitch.__instance = self

    def connect_usb_switch_port(self, device_name: str):
        """
        This method is used to connect the usb switch port.
        :param device_name: Name of the device which need to connect, This should be as per configuration file
            key "deviceName".
        :return: None
        :exception: AssertionError, SerialException, Exception
        """
        port_number = ""
        try:
            port_number = self.config_manager.get_port_number_for_name(device_name)
            if self.isOpen():
                ret = self.write(("o 0 " + str(port_number) + "\r").encode())
                response = self.read(ret+10).decode("utf-8")
                robot_print_info(f"USB Switch Response : {response}")
                match = re.search("[O&K][O&K]", response)
                if match:
                    robot_print_info(f"Response : {match}")
                assert match is not None, f"USB switch not connect with port {port_number}"
            else:
                robot_print_error(f"Serial port is close for the USB switch,"
                                  f" Can't able to connect the {device_name} and port: {self.path}")
        except AssertionError as assertion_error:
            robot_print_error(f"Assertion error to connect the usb port {port_number}, EXCEPTION: {assertion_error}")
        except SerialException as serial_exp:
            robot_print_error(f"Error to handle the serial port of USB switch to connect device {device_name}, "
                              f"EXCEPTION: {serial_exp}")
        except Exception as exp:
            robot_print_error(f"Error to connect the USB device: {exp}")

    def zilogic_disconnect_all_usb_port(self):
        try:
            if self.isOpen():
                ret = self.write("a\r".encode())
                assert ret == 2, "Error writing to usb switch while disconnecting."
            else:
                robot_print_error(f"Serial port is close for the USB switch,"
                                  f" Can't able to connect the {self.path}")
        except AssertionError as assertion_error:
            robot_print_error(
                f"Assertion error to disconnect all the USB port, EXCEPTION: {assertion_error}")
        except SerialException as serial_exp:
            robot_print_error(f"Error to handle the serial port of USB switch for disconnect all the device, "
                              f"EXCEPTION: {serial_exp}")
        except Exception as exp:
            robot_print_error(f"Error to disconnect all the USB device: {exp}")

    def switch_host(self, host_number: str):
        """
        This method is used to switch the host of Zilogic USB dual host Switch
        :param host_number: Host number in which user need to switch. it should be "0" or "1"
        :return:
        """
        try:
            if self.isOpen():
                ret = self.write(("h" + str(host_number) + "\r").encode())
                response = self.read(ret+10).decode("utf-8")
                robot_print_info(f"USB Switch Response : {response}")
                match = re.search("[O&K][O&K]", response)
                if match:
                    robot_print_info(f"Response : {match}")
                assert match is not None, f"USB switch not switch to host: {host_number}"
            else:
                robot_print_error(f"Port is close for path: {self.path}")
        except AssertionError as assertion_error:
            robot_print_error(
                f"Assertion error to switch USB host to {host_number}, EXCEPTION: {assertion_error}")
        except SerialException as serial_exp:
            robot_print_error(f"Error to handle the serial port of USB switch switch the host to {host_number}, "
                              f"EXCEPTION: {serial_exp}")
        except Exception as exp:
            robot_print_error(f"Error to switch the host in USB switch, EXCEPTION: {exp}")

    def disconnect_usb_switch_port(self, device_name):
        """
       This method is used to disconnect the usb switch port.
       :param device_name: Name of the device which need to disconnect, This should be as per configuration file
           key "deviceName".
       :return: None
       :exception: AssertionError, SerialException, Exception
       """
        port_number = ""
        try:
            port_number = self.config_manager.get_port_number_for_name(device_name)
            if self.isOpen():
                cmd = ("f 0" + str(port_number) + "\r")
                print(cmd)
                ret = self.write(cmd.encode())
                print(ret)
            else:
                raise SerialException(f"Port is close for path: {self.path}")
        except AssertionError as assertion_error:
            robot_print_error(f"Assertion error to disconnect the usb port {port_number}, EXCEPTION: {assertion_error}")
        except SerialException as serial_exp:
            robot_print_error(f"Error to handle the serial port of USB switch to disconnect device {device_name}, "
                              f"EXCEPTION: {serial_exp}")
        except Exception as exp:
            robot_print_error(f"Error to disconnect the {device_name} in USB switch: {exp}")

    def close(self):
        print("Calling close!")
        super(self.__class__, self).close()
