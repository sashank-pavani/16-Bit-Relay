"""
Lauterbach automation steps are added to this file.
Author: Sivakumar Ajeetha, Rajkumar Sruthi
Pre-requisite:
Limitations:
___________________________________________________________________
|     version 1.0.0      |  Lauterbach Utilization Basic methods are created.   |
-------------------------------------------------------------------
"""
import pyautogui
import win32gui
import win32con
from Robo_FIT.GenericLibraries.GenericOpLibs.Lauterbach.ConfigurationManager import *
from Robo_FIT.GenericLibraries.GenericOpLibs.Lauterbach.ConfigurationReader import *
import os
import time
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
import shutil
import sys
import subprocess
import time
import ctypes
import enum
import pygetwindow as gw
import tarfile
import win32gui
import win32con
import ctypes
import numpy as np
import glob
import cv2
import json
import datetime
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info
from glob import glob
from PIL import Image

class PracticeInterpreterState(enum.IntEnum):
    UNKNOWN = -1
    NOT_RUNNING = 0
    RUNNING = 1
    DIALOG_OPEN = 2


class MessageLineState(enum.IntEnum):
    ERROR = 2
    ERROR_INFO = 16


class Lauterbach:
    def __init__(self):
        self.api_config_file = None
        self.config_file = None
        self.config_manager = ConfiguratorManager()
        self.config_file = None
        self.api_config_file = None
        self.application_path = None
        self.startup_path = None
        self.cmm_script_path = None
        self.t32api = None
        self.cmm_script_state = None
        self.close_trace32 = None
        self.config_file_name = self.config_manager.get_config_file_name()
        self.config_file_path = self.config_manager.get_config_file_path()
        self.__create_api_config_file()
        self.trace32_path = self.config_manager.get_trace32_path()
        self.trace32_application = self.config_manager.get_application_name()
        self.device_id = self.config_manager.get_device_id()
        self.scripts_path = self.config_manager.get_vip_scripts_path()
        self.common_keyword = CommonKeywordsClass()

    def __create_api_config_file(self):
        """This method creates a copy of the config file with API access enabled for Launching and
        Accessing Trace32
        """
        try:
            self.config_file = os.path.join(self.config_file_path, self.config_file_name)
            self.api_config_file = "config_api.t32"
            source_config = self.config_file
            self.api_config = os.path.join(self.config_file_path, self.api_config_file)
            api_config_file_create = open(self.api_config, "w")
            api_config_file_create.close()
            api_config_file_creation = shutil.copyfile(self.config_file, self.api_config)
            robot_print_info("New config File created ", api_config_file_creation)
            with open(self.api_config, "a") as f:
                t32api_access = "\n;T32 API Access (UDP/TCP) \nRCL=NETASSIST \nPACKLEN=1024 \nPORT=20000"
                f.write(t32api_access)
            f.close()
            robot_print_info("API access lines are successfully added")
        except Exception as e:
            robot_print_error(f"Error to create a new config file for Trace32 api access, EXCEPTION: {e}")

    def trace32_launch(self):
        """This method launches Trace32 application by using the trace32 api remote access"""
        try:
            self.application_path = os.path.join(self.trace32_path + os.sep, 'bin', 'windows64',
                                                 self.trace32_application)
            self.startup_path = os.path.join(self.trace32_path + os.sep, 'demo', 'arm',
                                             'compiler', 'arm', 'cortexm.cmm')
            command = [self.application_path, '-c', self.api_config, '-s', self.startup_path]
            robot_print_info("Launching Trace32")
            process = subprocess.Popen(command)
            # Wait until the TRACE32 instance is started
            time.sleep(7)
            # Load TRACE32 Remote API
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            # Configure communication channel
            self.t32api.T32_Config(b"NODE=", b"localhost")
            self.t32api.T32_Config(b"PORT=", b"20000")
            self.t32api.T32_Config(b"PACKLEN=", b"1024")
            # Establish communication channel
            rc = self.t32api.T32_Init()
            rc = self.t32api.T32_Attach(self.device_id)
            rc = self.t32api.T32_Ping()
            robot_print_info("Trace32 Launched Successfully")
            return True
        except Exception as e:
            robot_print_error(f"Error to Launch Trace32, EXCEPTION: {e}")
            return False

    def run_cmm_script(self, script_name: str):
        """This method runs the cmm script"""
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            self.cmm_script_path = os.path.join(self.scripts_path, script_name)
            robot_print_info(f"The script path is {self.cmm_script_path}")
            cmm_command = "CD.DO" + " " + self.cmm_script_path
            changed_bytes = cmm_command.encode('utf-8')
            robot_print_info(f"command is {changed_bytes}")
            self.t32api.T32_Cmd(changed_bytes)

            time.sleep(5)
            return True
        except Exception as e:
            robot_print_error(f"Error to Run the script {script_name}, EXCEPTION: {e}")
            return False

    def set_dialog_box(self, option_number=None, button=None):
        "This method handles the dialog box automation"
        try:
            if option_number is not None:
                option_command = "DIALOG.SET Option." + option_number
                changed_option_bytes = option_command.encode('utf-8')
                self.t32api.T32_Cmd(changed_option_bytes)
                robot_print_info("Option set successfully")
            if button is not None:
                button_command = "DIALOG.EXECUTE" + " " + button
                changed_button_bytes = button_command.encode('utf-8')
                self.t32api.T32_Cmd(changed_button_bytes)
                robot_print_info("Button set successfully")
            else:
                robot_print_info("No Option or Button input received")
            return True
        except Exception as e:
            robot_print_error(f"Error to set the dialog box, EXCEPTION: {e}")
            return False


    def run_secure_cmm_script1(self, script_name: str):
        """This method runs the cmm script"""
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            self.cmm_script_path = os.path.join(self.scripts_path, script_name)
            robot_print_info(f"The script path is {self.cmm_script_path}")
            cmm_command = "CD.DO" + " " + self.cmm_script_path
            changed_bytes = cmm_command.encode('utf-8')
            robot_print_info(f"command is {changed_bytes}")
            self.t32api.T32_Cmd(changed_bytes)

            # Wait for the dialog box to appear
            time.sleep(5)

            # Automate the dialog box interaction
            pyautogui.press('Yes')  # Assuming 'Enter' selects 'Yes'

            return True
        except Exception as e:
            robot_print_error(f"Error to Run the script {script_name}, EXCEPTION: {e}")
            return False

    def run_secure_cmm_script(self, script_name: str):
        """This method runs the cmm script"""
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            self.cmm_script_path = os.path.join(self.scripts_path, script_name)
            robot_print_info(f"The script path is {self.cmm_script_path}")
            cmm_command = "CD.DO" + " " + self.cmm_script_path
            changed_bytes = cmm_command.encode('utf-8')
            robot_print_info(f"command is {changed_bytes}")
            self.t32api.T32_Cmd(changed_bytes)

            # Wait for the dialog box to appear
            time.sleep(5)  # Adjust this time as necessary

            # Press the "Enter" key
            pyautogui.press('enter')

            return True
        except Exception as e:
            robot_print_error(f"Error to Run the script {script_name}, EXCEPTION: {e}")
            return False
    def trace32_attach(self):
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            # Define the SYStem.Attach command
            attach_command = b"SYStem.Attach"

            # Execute the command using T32_Cmd
            result = self.t32api.T32_Cmd(attach_command)
            if result != 0:
                robot_print_info("SYStem.Attach failed")
                return False
            else:
                robot_print_info("SYStem.Attach successful")
                return True
        except Exception as e:
            robot_print_error(f"Error to complete Attach operation in Trace32, EXCEPTION: {e}")
            return False

    def read_var(self, var_name: str):
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            vvalue = ctypes.c_uint16(0)
            vvalueh = ctypes.c_uint16(0)
            rc = self.t32api.T32_ReadVariableValue(var_name, ctypes.byref(vvalue), ctypes.byref(vvalueh))
            if rc == 0:
                return vvalue.value
        except Exception as exp:
            robot_print_info(f"Read Variable not successful: {exp}")
            return False

    def trace32_reset(self):
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            reset_status = self.t32api.T32_ResetCPU()
            return True
        except Exception as exp:
            robot_print_info(f"Target Reset not successful: {exp}")
            return False

    def closethepopup(self):
        try:
            # Allow some time for the popup to appear
            time.sleep(2)  # Adjust the delay if necessary

            # Optionally, search for specific elements in the popup (you can also use OCR libraries like pytesseract to find text in the popup if needed)
            # For simplicity, let's assume the Enter key will dismiss the popup
            pyautogui.press('enter')  # Press "Enter" to select 'Yes' or 'OK'
            robot_print_info("Popup closed successfully.")
            return True
        except Exception as exp:
            robot_print_info(f"Error closing the popup: {exp}")
            return False
    def trace32_close(self):
        """This method is used to close the trace32 application"""
        try:
            t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            self.t32api = ctypes.cdll.LoadLibrary(t32api64)
            """Close trace32"""
            self.close_trace32 = self.t32api.T32_Cmd(b"QUIT")
            """Release communication channel"""
            rc = self.t32api.T32_Exit()
        except Exception as e:
            robot_print_error(f"Error to close the trace32, EXCEPTION: {e}")

    def loadfile(self, varpath):
        file = os.path.join(varpath)
        try:
            open(varpath)
            return True
        except Exception as exp:
            robot_print_info(f"file not opened properly : {exp}")
            return False

    def closethepopup(self):
        try:
            pyautogui.press('enter')
            return True
        except Exception as exp:
            robot_print_info(f"keyboard key not press not successful : {exp}")
            return False

    def load_srec_file(self, srec_file_path):
        """Load an .srec file into Trace32."""
        t32api64 = os.path.join(self.trace32_path + os.sep, 'demo', 'api', 'capi', 'dll', 't32api64.dll')
        self.t32api = ctypes.cdll.LoadLibrary(t32api64)
        if not os.path.isfile(srec_file_path):
            print(f"Error: The file '{srec_file_path}' does not exist.")
            return

        # Load the .srec file
        command = f"Data.LOAD.SREC {srec_file_path}"
        self.t32api.cmd(command)
        print(f"Loaded .srec file: {srec_file_path}")



    def close_t32_application(self):
        window_title = "TRACE32 PowerView for ARM #1"
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        else:
            print("Window not found!")

    @staticmethod
    def t32_state():
        """
        Method created to confirm the state of Trace32.
        :param :None.
        :return: True if Trace32 does not have any errors, False if any errors are available.
        """
        try:
            # Load TRACE32 Remote API
            t32api64 = os.path.join('C:' + os.sep, 'T32', 'demo', 'api', 'capi', 'dll', 't32api64.dll')
            t32api = ctypes.cdll.LoadLibrary(t32api64)
            script_status = ctypes.c_uint16(-1)
            rc = t32api.T32_EvalGet(ctypes.byref(script_status))
            if rc == 0 and script_status.value == 0:
                robot_print_info("script ran properly")
                return True
        except Exception as exp:
            robot_print_info(f"Exception to find t32 state:{exp}")
            return False



if __name__ == '__main__':
    v = Lauterbach()
    # v.trace32launch()
    # v.quit_trace32()
    v.trace32_launch()
    v.run_cmm_script()
    v.trace32_close()
