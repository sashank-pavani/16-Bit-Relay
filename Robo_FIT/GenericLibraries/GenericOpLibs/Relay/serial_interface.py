#!/usr/bin/python

import serial.tools.list_ports
import os, sys


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
            usb_serial_devices = str(usb_serial_devices.strip())
            if device in usb_serial_devices:
                device_flag = True
                return port

    if not device_flag:
        os.system("echo Check Configuration File path in Project Config File or Relay not connected...!!!")