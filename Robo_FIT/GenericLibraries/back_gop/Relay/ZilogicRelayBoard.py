#!/usr/bin/env python
from time import sleep

from serial import Serial
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.ConfiguratorManager import ConfiguratorManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.IRelay import IRelay
from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.serial_interface import _get_device_from_script


class ZilogicRelayBoard(Serial, IRelay):
    """ Class exposing interface to Zilogic USB Relay controller connected to Zilogic ZA-RLY4X12V-P1-R1B."""
    __instance = None

    @staticmethod
    def get_relay_instance():
        """
        This method return the only single object of Relay Class
        :param path: path of serial port
        :param baudrate: baudrate of the device.
        :return: single object of Relay call
        """
        if ZilogicRelayBoard.__instance is None:
            ZilogicRelayBoard()
        return ZilogicRelayBoard.__instance

    def __init__(self):
        if ZilogicRelayBoard.__instance is not None:
            raise Exception("This is a Relay class")
        else:
            self.config_manager = ConfiguratorManager()
            self.path = _get_device_from_script(self.config_manager.get_device_id())
            super(self.__class__, self).__init__(port=self.path,
                                                 baudrate=self.config_manager.get_baud_rate())
            ZilogicRelayBoard.__instance = self

    def __switch_relay(self, relay_id: str, action: str):
        """
        This method is used to connect and disconnect the relay port base the user action.
        :param relay_id: Port number need to be disconnect
        :param action: ON if your want to on the given port, otherwise OFF.
        :return: None
        :raise: ValueError, AssertionError
        """

        if action.upper() != 'ON' and action.upper() != 'OFF':
            raise ValueError("Invalid action inputs to relay_box")

        if (self.isOpen()):
            sleep(0.3)
            ret = self.write((("S" if action == 'ON' else "C") + relay_id + "\r\n").encode())
        else:
            raise AssertionError("Relay board port %s is closed.")

        assert ret == 4, "Error writing to serial port for relay: %s" % relay_id

    def connect_relay_port(self, device_name: str):
        """
        This method is used to connect the relay port.
        :param device_name: Name of the device need to connect .
                            This name should be base on the configuration key "cntDeviceName"
        :return: None
        :exception: This will handle ValueError, AssertionError and Generic Exception.
        """
        try:
            port_number = self.config_manager.get_port_no(device=device_name)
            self.__switch_relay(port_number, "ON")
        except ValueError as value_error:
            robot_print_error(f"Exception to connect the device, EXCEPTION: {value_error}")
        except AssertionError as assertion_error:
            robot_print_error(f"Assertion Error in connect the relay, EXCEPTION: {assertion_error}")
        except Exception as exp:
            robot_print_error(f"Something went wrong to connect the relay port please check the log, EXCEPTION: {exp}")

    def disconnect_relay_port(self, device_name: str):
        """
        This method is used to disconnect the relay port.
        :param device_name: Name of the device need to disconnect .
                            This name should be base on the configuration key "cntDeviceName"
        :return: None
        :exception: This will handle ValueError, AssertionError and Generic Exception.
        """
        try:
            port_number = self.config_manager.get_port_no(device=device_name)
            self.__switch_relay(port_number, "OFF")
        except ValueError as value_error:
            robot_print_error(f"Exception to disconnect the device, EXCEPTION: {value_error}")
        except AssertionError as assertion_error:
            robot_print_error(f"Assertion Error in connect the device, EXCEPTION: {assertion_error}")
        except Exception as exp:
            robot_print_error(f"Something went wrong to disconnect the relay port please check the log, EXCEPTION: {exp}")

    def close(self):
        """
        Use to close the relay port.
        :return:
        """
        print("Calling close!")
        super(self.__class__, self).close()
