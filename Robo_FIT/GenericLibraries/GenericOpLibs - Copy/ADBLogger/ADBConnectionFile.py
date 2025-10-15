import subprocess
from time import sleep
import os
import re
from typing import List

from Robo_FIT.GenericLibraries.GenericOpLibs.ADBLogger.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_warning
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info


class ADBConnectionFile:
    DEVICE_ONLINE = "online"
    DEVICE_OFFLINE = "offline"

    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.hardware_id = self.config_manager.get_adb_network_id()
        self.hardware_adb_id = self.config_manager.get_adb_usb_id()
        #  split the hardware to get the TCP/IP port number
        if ":" in self.hardware_id:
            tcpip_port = self.hardware_id.split(":")
            self.tcpip_port_number = tcpip_port[1]
        else:
            self.tcpip_port_number = ""

    def __convert_offline_device_online(self):
        adb_kill = self.__subprocess_cmd_output("adb kill-server")
        if adb_kill == "":
            self.__execute_adb_tcpip()
            self._execute_adb_connect()
        else:
            robot_print_error("Some problem to kill the adb server!!!!!!!!", print_in_report=True)

    def __subprocess_cmd_output(self, cmd: str) -> str:
        """
        This is the documentation of this method.
        This method is used to run the command using subprocess
        :exception: OSError, if there is error to execute command
        :param cmd: command to be execute
        :raises: None
        :return: Output of the string
        """
        try:
            robot_print_debug("Start to execute command :  %s" % cmd)
            cmd_output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sleep(2)
            output, error = cmd_output.communicate()
            return output.decode('utf-8')
        except Exception as exception:
            robot_print_error(f"error to connect adb over wifi, EXCEPTION: {exception}", print_in_report=True)
            return ""

    def get_devices_list(self, adb_path='adb') -> List:
        """
        This method return the list of the available devices.
        :param adb_path: Option argument, Path of the adb.exe. If its in environment variable then
        no need to pass the argument
        :return: List of available ADB devices
        """
        try:
            with open(os.devnull, 'wb') as devnull:
                subprocess.check_call([adb_path, 'start-server'], stdout=devnull,
                                      stderr=devnull)
            out = self._split_lines(
                subprocess.check_output([adb_path, 'devices']).decode('utf-8'))
            # The first line of `adb devices` just says "List of attached devices", so
            # skip that.
            devices = []
            for line in out[1:]:
                if not line.strip():
                    continue
                if 'offline' in line:
                    continue
                serial, _ = re.split(r'\s+', line, maxsplit=1)
                devices.append(serial)
            return devices
        except Exception as exp:
            robot_print_error(f"Error to get the ADB device list, EXCEPTION: {exp}")

    def _split_lines(self, s: str) -> List:
        """Splits lines in a way that works even on Windows and old devices.
        Windows will see \r\n instead of \n, old devices do the same, old devices
        on Windows will see \r\r\n.
        """
        return re.split(r'[\r\n]+', s.rstrip())

    def __execute_adb_tcpip(self):
        tcpip_cmd = "adb -s \"{deviceId}\" tcpip {port}".format(port=self.tcpip_port_number,
                                                                deviceId=self.hardware_adb_id)
        tcpip_output = self.__subprocess_cmd_output(tcpip_cmd)
        robot_print_debug("tcpip command output is : %s" % tcpip_output)
        # check the output of the command if successfully restart tcpip then try to connect
        # adb over wifi otherwise print error
        outstr = "restarting in TCP mode port: {port}".format(port=self.tcpip_port_number)
        is_tcpip_execute = False
        # if tcpip command return empty output then retry
        if tcpip_output.strip() == "":
            # loop of restarting port ADB TCPIP
            for i in range(0, 5):
                robot_print_debug(
                    "Unable to execute the \"adb tcpip\" commnad.\n Retrying to connect({n}/5).....".format(n=i))
                sleep(2)
                tcpip_output = self.__subprocess_cmd_output(tcpip_cmd)
                sleep(2)
                robot_print_debug("After retry adb tcpip, tcpip command output is : %s" % tcpip_output)
                if tcpip_output.strip() == outstr.strip():
                    is_tcpip_execute = True
                    break
                else:
                    is_tcpip_execute = False
        elif tcpip_output.strip() == outstr.strip():
            is_tcpip_execute = True

        return is_tcpip_execute

    def _execute_adb_connect(self):
        wifi_connect_cmd = "adb -s \"{deviceId}\" connect {ip}".format(
            deviceId=self.hardware_adb_id,
            ip=self.hardware_id)
        # execute the command "adb connect <url>"
        wifi_connect_output = self.__subprocess_cmd_output(wifi_connect_cmd)
        # check is adb connect command unable to connect adb over wifi
        # Flag to check adb connect command execute successfully or failed
        is_adb_connect_execute = False
        # check adb connect execute successfully or not
        # if adb not already connected and return empty string then try to connect it over wifi
        if not wifi_connect_output.strip() == "already connected to {ip}".format(ip=self.hardware_id).strip()\
                and wifi_connect_output.strip() != "connected to {ip}".format(ip=self.hardware_id).strip():
            # try five times to connect adb over wifi
            for i in range(0, 5):
                robot_print_debug(
                    "Unable to execute the \"adb connect {port}\" commnad.\n Retrying to connect({n}/5).....".format(
                        port=self.hardware_id, n=i))
                # execute the adb connect command
                wifi_connect_output = self.__subprocess_cmd_output(wifi_connect_cmd)
                # check if it connect successfully OR not
                if wifi_connect_output.strip() == "connected to {ip}".format(ip=self.hardware_id).strip():
                    # if successfully connect assign TRUE to flag isAdbConnectExecute and break the loop
                    is_adb_connect_execute = True
                    break
                # if adb already connected to over wifi
                elif wifi_connect_output.strip() == "already connected to {ip}".format(ip=self.hardware_id).strip():
                    device_list = self.get_devices_list()
                    if self.hardware_id in device_list:
                        is_adb_connect_execute = True
                    else:
                        robot_print_error("Device not found...!!!")
                else:
                    robot_print_error("Sorry we are unable to connect adb over wifi. Please Retry...!!!!")
        else:
            is_adb_connect_execute = True
        return is_adb_connect_execute

    def connect_hardware_ip_adb(self):
        """
        This method is used to connect the ADB device over NETWORK.
        It fetch the "adbId"(which is a TCP/IP address of target) from the configuration file and connect it.
        :return: None
        """
        robot_print_debug("Available Device's list \n%s" % self.get_devices_list(), print_in_report=True)
        if self.tcpip_port_number != "":
            devices_list = self.get_devices_list()
            if self.hardware_id in devices_list:
                robot_print_info("Device already connected...!!!")
            else:
                if self.__disconnect_device():
                    self.__connect_adb_network_device()
                else:
                    robot_print_warning("Fail to Disconnect the device first, but try to connect", print_in_report=True)
                    self.__connect_adb_network_device()
        else:
            robot_print_error("User not provide any TCP/IP address in configuration file", print_in_report=True)

    def __connect_adb_network_device(self):
        adb_connect_cmd = "adb connect {ip}".format(ip=self.hardware_id)
        adb_connect_output = self.__subprocess_cmd_output(adb_connect_cmd)
        if "failed to connect" in adb_connect_output:
            robot_print_debug(adb_connect_output)
            self.__retry_to_connect(adb_connect_cmd=adb_connect_cmd)
        elif f"cannot connect to {self.hardware_id}" in adb_connect_output:
            self.__retry_to_connect(adb_connect_cmd=adb_connect_cmd)
        else:
            robot_print_debug(adb_connect_output)
            robot_print_info("Hardware is connected successfully.....", print_in_report=True)

    def __retry_to_connect(self, adb_connect_cmd: str):
        for i in range(0, 5):
            robot_print_debug(f"Number of retry for connect the ADB device {self.hardware_id}: {i}")
            adb_connect_output = self.__subprocess_cmd_output(adb_connect_cmd)
            robot_print_debug(adb_connect_output, print_in_report=True)
            if "failed to connect" not in adb_connect_output:
                robot_print_debug(adb_connect_output, print_in_report=True)
            elif f"cannot connect to {self.hardware_id}" in adb_connect_output:
                robot_print_debug(adb_connect_output, print_in_report=True)
            elif f"connected to {self.hardware_id}" in adb_connect_output:
                robot_print_debug(adb_connect_output, print_in_report=True)
                robot_print_info("Hardware is connected successfully.....", print_in_report=True)
                break
            sleep(0.5)
        robot_print_error("Can't Connect with hardware After 5 retries....!!!", print_in_report=True)

    def __disconnect_device(self) -> bool:
        """
        This methods disconnect ADB device.
        :return:
        """
        if self.hardware_id in self.get_devices_list():
            return True
        else:
            adb_disconnect_cmd = "adb disconnect {ip}".format(ip=self.hardware_id)
            adb_disconnect_output = self.__subprocess_cmd_output(adb_disconnect_cmd)
            if "disconnected" in adb_disconnect_output:
                robot_print_debug(adb_disconnect_output)
                return True
            elif "error: no such device" in adb_disconnect_output:
                robot_print_debug(adb_disconnect_output)
                return True
            else:
                robot_print_debug(adb_disconnect_output)
                robot_print_error("Error to Connect the ADB Device", print_in_report=True)
                return False

    def stop_crash_logs_thread(self):
        """
        This method is used to stop the crash logs and the thread which get the
        crash logs data
        :exception: OSError
        :return: None
        """
        try:
            sleep(10)
            if self.tcpip_port_number == "":
                robot_print_debug("Wait for sometime.... Stoping Crash logs")
                subprocess.Popen("adb kill-server", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                sleep(5)
                subprocess.Popen("adb start-server", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                sleep(5)
                robot_print_debug("Device Lists")
                out = subprocess.Popen("adb start-server", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                output, error = out.communicate()
                if not error:
                    robot_print_debug(output.decode("utf-8"))
                robot_print_debug(str(self.get_devices_list()))
                robot_print_info("Crash logs Stop")
            else:
                robot_print_debug("Wait for sometime.... Stoping Crash logs")
                adb_disconnect_cmd = "adb disconnect {ip}".format(ip=self.hardware_id)
                self.__subprocess_cmd_output(adb_disconnect_cmd)
                sleep(5)
                adb_connect_cmd = "adb connect {ip}".format(ip=self.hardware_id)
                self.__subprocess_cmd_output(adb_connect_cmd)
                robot_print_debug(str(self.get_devices_list()))
                robot_print_info("Crash logs Stop")

        except Exception as err:
            robot_print_error(f"There is an error to stop the crash logs, EXCEPTION: {err}", print_in_report=True)

    def kill_adb_server(self):
        self.__subprocess_cmd_output("adb kill-server")
        sleep(2)
        self.__subprocess_cmd_output("adb start-server")
        sleep(1)
        self.connect_hardware_ip_adb()

    def get_adb_device_status(self, device_id: str) -> str:
        """
        This function is used to check given android device status using the device id.
        :param device_id: Android device id
        :type device_id: String
        :return: It will return the status of the device
        Status should be :
            ADBConnectionFile.DEVICE_ONLINE
            ADBConnectionFile.DEVICE_OFFLINE
        :rtype: String
        """
        try:
            out = subprocess.check_output(['adb', 'devices'])
            out = str(out.decode('utf-8'))
            devices = re.split(r'\r\n+', out.rstrip())
            for line in devices[1:]:
                if device_id in line:
                    if 'offline' in line:
                        return ADBConnectionFile.DEVICE_OFFLINE
                    elif 'unauthorised' in line:
                        return ADBConnectionFile.DEVICE_OFFLINE
                    elif 'device' in line:
                        return ADBConnectionFile.DEVICE_ONLINE
                    else:
                        return ADBConnectionFile.DEVICE_OFFLINE
            return ADBConnectionFile.DEVICE_OFFLINE
        except OSError as exp:
            robot_print_error(f"Error to check the adb device status: {exp}")
