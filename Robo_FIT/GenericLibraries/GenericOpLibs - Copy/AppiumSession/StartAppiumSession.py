import time
import os
import sys
import subprocess
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.AppiumSession.ConfigurationManager import ConfigurationManager


class StartAppiumSession:

    def __init__(self):
        self.__close_appium_session()  # use to close the appium session before creating new session
        self.config_manager = ConfigurationManager()
        self.checking_flag = False
        self.hardware_appium_port = self.config_manager.get_hardware_port()
        self.bt_phone_one_appium_port = self.config_manager.get_bt_device_one_port()
        self.bt_phone_two_appium_port = self.config_manager.get_bt_device_two_port()
        self.bt_phone_three_appium_port = self.config_manager.get_bt_device_three_port()
        self.bt_phone_four_appium_port = self.config_manager.get_bt_device_four_port()

    def start_appium_session(self):
        """
        This method is run the appium session. It read the port number form the
        configuration files and run the session.
        :return: None
        """
        try:
            if sys.platform.startswith('linux'):
                adbdevice = subprocess.Popen(["adb devices"], shell=True, stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
                out, err = adbdevice.communicate()
                robot_print_debug("before appium start adb devices:\n %s" % out.decode('utf-8'))
            elif sys.platform.startswith("win32"):
                robot_print_debug("before appium start adb devices:\n %s" % os.system("adb devices"))
            if self.config_manager.get_hardware_port() != "":
                if self.hardware_appium_port != "":
                    appium_session_hardware = ""
                    if sys.platform.startswith('linux'):
                        appium_session_hardware = "gnome-terminal -- bash -c \"appium --relaxed-security -p {port};exec bash\"".format(
                            port=self.hardware_appium_port)
                    elif sys.platform.startswith('win32'):
                        appium_session_hardware = "start cmd.exe @cmd /k \"appium --relaxed-security -p {port}\"".format(
                            port=self.hardware_appium_port)
                    os.system(appium_session_hardware)
                    time.sleep(20)
                    self.__check_appium_session(str(self.hardware_appium_port))
                else:
                    robot_print_error("You not provide the appium port number for the W601", print_in_report=True)

            if self.config_manager.get_bt_device_one_port() != "":
                if self.bt_phone_one_appium_port != "":
                    appium_session_one = ""
                    if sys.platform.startswith('linux'):
                        appium_session_one = "gnome-terminal -- bash -c \"appium --relaxed-security -p {port};exec bash\"".format(
                            port=self.bt_phone_one_appium_port)
                    elif sys.platform.startswith("win32"):
                        appium_session_one = "start cmd.exe @cmd /k \"appium --relaxed-security -p {port}\"".format(
                            port=self.bt_phone_one_appium_port)
                    os.system(appium_session_one)
                    time.sleep(20)
                    self.__check_appium_session(str(self.bt_phone_one_appium_port))
                else:
                    robot_print_error("You not provide the appium port number for the BT Phone One Device Name",
                                      print_in_report=True)

            if self.config_manager.get_bt_device_two_port() != "":
                if self.bt_phone_two_appium_port != "":
                    appium_session_two = ""
                    if sys.platform.startswith('linux'):
                        appium_session_two = "gnome-terminal -- bash -c \"appium --relaxed-security -p {port};exec bash\"".format(
                            port=self.bt_phone_two_appium_port)
                    elif sys.platform.startswith("win32"):
                        appium_session_two = "start cmd.exe @cmd /k \"appium --relaxed-security -p {port}\"".format(
                            port=self.bt_phone_two_appium_port)
                    os.system(appium_session_two)
                    time.sleep(20)
                    self.__check_appium_session(str(self.bt_phone_two_appium_port))
                else:
                    robot_print_error("You not provide the appium port number for the BT Phone Two Device Name",
                                      print_in_report=True)

            if self.config_manager.get_bt_device_three_port() != "":
                if self.bt_phone_three_appium_port != "":
                    appium_session_three = ""
                    if sys.platform.startswith('linux'):
                        appium_session_three = "gnome-terminal -- bash -c \"appium --relaxed-security -p {port};exec bash\"".format(
                            port=self.bt_phone_three_appium_port)
                    elif sys.platform.startswith("win32"):
                        appium_session_three = "start cmd.exe @cmd /k \"appium --relaxed-security -p {port}\"".format(
                            port=self.bt_phone_three_appium_port)
                    os.system(appium_session_three)
                    time.sleep(20)
                    self.__check_appium_session(str(self.bt_phone_three_appium_port))
                else:
                    robot_print_error("You not provide the appium port number for the BT Phone Three Device Name",
                                      print_in_report=True)

            if self.config_manager.get_bt_device_four_port() != "":
                if self.bt_phone_four_appium_port != "":
                    appium_session_four = ""
                    if sys.platform.startswith('linux'):
                        appium_session_four = "gnome-terminal -- bash -c \"appium --relaxed-security -p {port};exec bash\"".format(
                            port=self.bt_phone_four_appium_port)
                    elif sys.platform.startswith("win32"):
                        appium_session_four = "start cmd.exe @cmd /k \"appium --relaxed-security -p {port}\"".format(
                            port=self.bt_phone_four_appium_port)
                    os.system(appium_session_four)
                    time.sleep(20)
                    self.__check_appium_session(str(self.bt_phone_four_appium_port))
                else:
                    robot_print_error("You not provide the appium port number for the BT Phone Four Device Name",
                                      print_in_report=True)
        except OSError as ex:
            robot_print_error(f"Error to execute the OS commands, EXCEPTION: {ex}", print_in_report=True)

    def __check_appium_session(self, port_number: str) -> bool:
        """
        This method check that given port is available/free or not and start the appium session.
        :param port_number: Port number if which user want to run the session.
        :return: If session start it return True, else it will close the program
        """
        cmd = ""
        if sys.platform.startswith('linux'):
            cmd = "netstat -antu | grep {port}".format(port=port_number)
        elif sys.platform.startswith('win32'):
            cmd = "netstat -ano | findstr {port}".format(port=port_number)
        for _ in range(0, 2):
            chk_command = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            cmd_output, err = chk_command.communicate()
            logger.console(f"Appium port started at  {cmd_output.decode('utf-8')}")
            if port_number not in cmd_output.decode('utf-8'):
                robot_print_error(f"There is an error to open the appium session at Port number {port_number}, "
                                  f"EXCEPTION: {err}", print_in_report=True)
            else:
                robot_print_info(f"Appium session in Port Number {port_number} is started successfully,",
                                 print_in_report=True)
                self.checking_flag = True
                return self.checking_flag
            time.sleep(5)
        sys.exit("It seem appium port is not open after trying 3 times,"
                 " Please check appium is properly install on your system.")

    def hardware_appium_url(self) -> str:
        """
        This method return the URL for the user so that they can send
        appium related request.
        :return: None
        """
        if self.hardware_appium_port != "":
            url = "http://127.0.0.1:{port}/wd/hub".format(port=self.hardware_appium_port)
            return url

    def ext_phone_one_appium_url(self) -> str:
        """
        This method return the URL for the user so that they can send
        appium related request.
        :return: None
        """
        if self.bt_phone_one_appium_port != "":
            url = "http://127.0.0.1:{port}/wd/hub".format(port=self.bt_phone_one_appium_port)
            return url

    def ext_phone_two_appium_url(self) -> str:
        """
        This method return the URL for the user so that they can send
        appium related request.
        :return: None
        """
        if self.bt_phone_two_appium_port != "":
            url = "http://127.0.0.1:{port}/wd/hub".format(port=self.bt_phone_two_appium_port)
            return url

    def ext_phone_three_appium_url(self) -> str:
        """
        This method return the URL for the user so that they can send
        appium related request.
        :return: None
        """
        if self.bt_phone_three_appium_port != "":
            url = "http://127.0.0.1:{port}/wd/hub".format(port=self.bt_phone_three_appium_port)
            return url

    def ext_phone_four_appium_url(self) -> str:
        """
        This method return the URL for the user so that they can send
        appium related request.
        :return: None
        """
        if self.bt_phone_four_appium_port != "":
            url = "http://127.0.0.1:{port}/wd/hub".format(port=self.bt_phone_four_appium_port)
            return url

    def __close_appium_session(self):
        """
        This method close the all the previous appium session.
        If appium session in same port which user mention in configuration file
        then is cause the problem the its need to close that session first.
        :return: None
        """
        try:
            if sys.platform.startswith("linux"):
                os.system("killall node")
            elif sys.platform.startswith('win32'):
                os.system("taskkill /IM \"node.exe\" /F")
        except OSError as excep:
            robot_print_error(f"Error to kill the appium session.{excep}")
