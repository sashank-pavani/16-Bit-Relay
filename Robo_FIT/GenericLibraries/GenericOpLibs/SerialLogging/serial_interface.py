#!/usr/bin/python

import serial.tools.list_ports
import os, sys

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info


def _get_device_from_script(*devices):
    """
    This method is used to provide the device path acc. to the device id
    For eg.: /dev/ttyUSB0
    :param devices: a unique id of that device
    :return: device port path
    """
    ports = serial.tools.list_ports.comports(include_links=False)
    lines = []
    device_flag = False
    for device in devices:
        for port, desc, hwid in sorted(ports):
            usb_serial_devices = ("{}: {} {}".format(port, desc, hwid))
            robot_print_info(f"Available devices are : {usb_serial_devices}, Please use any of them")
            robot_print_info(f"for Device :{hwid}, the Port is : {port}")
            usb_serial_devices = str(usb_serial_devices.strip())
            if device in usb_serial_devices:
                device_flag = True
                return port
            else:
                robot_print_info(f"{device} not in {usb_serial_devices}, Unable to return Port")

    if not device_flag:
        os.system("echo Check Configuration File path in Project Config File or Serial Board not connected...!!!")

