import serial
from serial import Serial, SerialException
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ASTART_GSM
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug, robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.serial_interface import _get_device_from_script
from Robo_FIT.GenericLibraries.GenericOpLibs.GSMModule.IGsmModule import IGsmModule


class AstarGSMModule(IGsmModule):
    """ Class exposing interface to Astar GSM Module."""
    __instance = None

    @staticmethod
    def get_gsm_instance():
        if AstarGSMModule.__instance is None:
            AstarGSMModule()
        return AstarGSMModule.__instance

    def __init__(self):
        if AstarGSMModule.__instance is not None:
            raise Exception("This is a GSM class")
        else:
            self.config_manager = ConfigurationManager()
            AstarGSMModule.__instance = self

    def gsm_send_message(self, gsm_num, recipient, message):
        """Send message
        Send message to the RECIPIENT with content in the message variable
        """
        try:
            path = _get_device_from_script(self.config_manager.read_gsm_device_id(device_num=gsm_num))
            serial_obj = Serial(port=path, baudrate=self.config_manager.read_baudrate())
            if serial_obj.isOpen():
                sleep(0.5)
                serial_obj.write('ATZ\r'.encode())
                sleep(0.5)
                serial_obj.write('AT+CMGF=1\r'.encode())
                sleep(0.5)
                serial_obj.write('AT+CMGS="'.encode() + recipient.encode() + '"\r'.encode())
                sleep(0.5)
                serial_obj.write(message.encode() + "\r".encode())
                sleep(0.5)
                serial_obj.write(chr(26).encode())
                sleep(0.5)
            else:
                robot_print_error(f"Serial port close for send message using Astar GSM module,"
                                  f"Please check the device id in configuration file")
        except SerialException as serial_err:
            robot_print_error(f"Error to send message using GSM module, EXCEPTION: {serial_err}")

    def gsm_make_call(self, gsm_num, recipient):
        """Make Call

        Make a call to the number in RECIPIENT variable
        """
        try:
            path = _get_device_from_script(self.config_manager.read_gsm_device_id(device_num=gsm_num))
            serial_obj = Serial(port=path, baudrate=self.config_manager.read_baudrate())
            if serial_obj.isOpen():
                serial_obj.write('ATZ\r'.encode())  # ATZ : Restore profile
                sleep(0.5)
                serial_obj.write('ATD '.encode() + recipient.encode() + ';\r'.encode())
                sleep(0.5)
                serial_obj.write(chr(26).encode())
                sleep(0.5)
            else:
                robot_print_error(f"Serial port close for make call in Astar GSM module, Please check the device id in"
                                  f"configuration file")
        except SerialException as serial_err:
            robot_print_error(f"Error to make call using GSM module, EXCEPTION: {serial_err}")

    def gsm_end_call(self, gsm_num):
        """Disconnect Call

        Disconnect the incoming call which is currently active gms_in
        """
        try:
            path = _get_device_from_script(self.config_manager.read_gsm_device_id(device_num=gsm_num))
            serial_obj = Serial(port=path, baudrate=self.config_manager.read_baudrate())
            if serial_obj.isOpen():
                serial_obj.write('ATZ\r'.encode())
                sleep(0.5)
                serial_obj.write('AT+CHUP\r'.encode())
                sleep(0.5)
                serial_obj.write(chr(26).encode())
                sleep(0.5)
            else:
                robot_print_error(f"Serial port close for end call for Astar GSM module, Please check the device id in"
                                  f"configuration file")
        except SerialException as serial_err:
            robot_print_error(f"Error to end call using GSM module, EXCEPTION: {serial_err}")

    def gsm_answer_call(self, gsm_num):
        """Attend call

        Attend incoming call
        """
        try:
            path = _get_device_from_script(self.config_manager.read_gsm_device_id(device_num=gsm_num))
            serial_obj = Serial(port=path, baudrate=self.config_manager.read_baudrate())
            if serial_obj.isOpen():
                serial_obj.write('ATZ\r'.encode())
                sleep(0.5)
                serial_obj.write('ATA\r'.encode())
                sleep(0.5)
                serial_obj.write(chr(26).encode())
                sleep(0.5)
            else:
                robot_print_error(f"Serial port close for answer call Astar GSM module, Please check the device id in"
                                  f"configuration file")
        except SerialException as serial_err:
            robot_print_error(f"Error to answer call using GSM module, EXCEPTION: {serial_err}")

    def gsm_reject_call(self, gsm_num):
        """Reject call

        Reject incoming call
        """
        try:
            path = _get_device_from_script(self.config_manager.read_gsm_device_id(device_num=gsm_num))
            serial_obj = Serial(port=path, baudrate=self.config_manager.read_baudrate())
            if serial_obj.isOpen():
                serial_obj.write('ATZ\r'.encode())
                sleep(0.5)
                serial_obj.write('ATH\r'.encode())
                sleep(0.5)
                serial_obj.write(chr(26).encode())
                sleep(0.5)
            else:
                robot_print_error(f"Serial port close for reject call Astar GSM module, Please check the device id in"
                                  f"configuration file")
        except SerialException as serial_err:
            robot_print_error(f"Error to reject call using GSM module, EXCEPTION: {serial_err}")
