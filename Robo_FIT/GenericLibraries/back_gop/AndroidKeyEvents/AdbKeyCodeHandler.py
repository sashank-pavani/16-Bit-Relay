import re
import subprocess
import os
from time import sleep
from typing import List

from ppadb.client import Client as ADBClient
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidKeyEvents.ConfigurationManager import ConfigurationManager


class AdbKeyCodeHandler:
    setting = "SETTINGS"
    phone = "PHONE"
    media = "MEDIA"
    call = "CALL"
    favorite = "FAVORITE"
    source = "SOURCE"
    ok = "OK"
    up = "UP"
    right = "RIGHT"
    left = "LEFT"
    down = "DOWN"
    home = "HOME"
    back = "BACK"
    vol_up = "VOL_UP"
    vol_down = "VOL_DOWN"
    vol_mute = "VOL_MUTE"
    media_next = "MEDIA_NEXT"
    media_prev = "MEDIA_PREV"
    media_pause = "MEDIA_PAUSE"
    media_play = "MEDIA_PLAY"

    def __init__(self):
        try:
            self.config_manger = ConfigurationManager()
            self.device_id = self.config_manger.android_device_id()
            is_connected = False
            self.device = ADBClient().device(self.device_id)
            if self.device_id not in self.__get_devices_list():
                robot_print_error(
                    f"Error to initialize the AdbKeyCodeHandler class, EXCEPTION: Device {self.device_id} is not in connected device list")
        except Exception as exp:
            robot_print_error("Device not connect, EXCEPTION: %s" % exp)
            raise Exception("Please check device is connected or not")

    def __get_devices_list(self, adb_path='adb') -> List:
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call([adb_path, 'start-server'], stdout=devnull,
                                  stderr=devnull)
        out = self.__split_lines(
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

    def __split_lines(self, s):
        """Splits lines in a way that works even on Windows and old devices.
        Windows will see \r\n instead of \n, old devices do the same, old devices
        on Windows will see \r\r\n.
        """
        return re.split(r'[\r\n]+', s.rstrip())

    def __check_device_online(self) -> bool:
        try:
            if self.device_id not in self.__get_devices_list():
                return False
            return True
        except RuntimeError as run_err:
            robot_print_error(
                f"It seems device {self.device_id} is online or offline in AdbKeyCodeHandler, EXCEPTION: {run_err}")
        except Exception as exp:
            robot_print_error(f"Error to check that device is online or offline, EXCEPTION: {exp}")

    def __send_key_code(self, cmd_press: str, cmd_release: str = None, long_press: bool = False, duration: float = 0):
        """
        This methods is used to send the Android Key code to given device id
        :param: cmd_press: str, Command to press the key
        :param: cmd_release: str, Command to release the key
        :param: long_press: bool, True if long press otherwise false. Default False
        :param: duration: float, Duration in float seconds for long press. Default 0
        """
        try:
            if self.__check_device_online():
                if cmd_press is not None and cmd_release is not None:
                    if long_press:
                        robot_print_info(f"long press event for : {cmd_press}")
                        self.device.shell(cmd_press)
                        sleep(1 if duration == 0 else duration)
                        robot_print_info(cmd_release)
                        self.device.shell(f"long press event for : {cmd_release}")

                    else:
                        robot_print_info(cmd_press)
                        self.device.shell(cmd_press)
                        robot_print_info(cmd_release)
                        self.device.shell(cmd_release)
                elif cmd_press is not None and cmd_release is None:
                    robot_print_info(cmd_press)
                    self.device.shell(cmd_press)
                else:
                    robot_print_error("Please provide the Key codes in config file")
        except Exception as exp:
            robot_print_error(f"Error to execute the keycode commands, EXCEPTION: {exp}")

    def swc_adb_volume_event(self, event: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC  key event in given Android ID(which user pass in config file)
        This method send the
            1. Volume UP
            2. Volume DOWN
            3. Volume MUTE
        :param event: (String) event to send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = None
            cmd_release = None
            if event == AdbKeyCodeHandler.vol_up:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.volume_up_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.volume_up_key_code())
            elif event == AdbKeyCodeHandler.vol_down:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.volume_down_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.volume_down_key_code())
            elif event == AdbKeyCodeHandler.vol_mute:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.volume_mute_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.volume_mute_key_code())
            else:
                robot_print_error("%s is not a known event, please configure this event or ask automation framework"
                                  " developer for more help" % event)
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_media_event(self, event: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC  key event in given Android ID(which user pass in config file)
        This method send the
            1. Media Play
            2. Media Pause
            3. Media Next
            4. Media Previous
        :param event: (String) event to send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = None
            cmd_release = None
            if event == AdbKeyCodeHandler.media_pause:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.media_pause_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.media_pause_key_code())
            elif event == AdbKeyCodeHandler.media_play:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.media_play_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.media_play_key_code())
            elif event == AdbKeyCodeHandler.media_next:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.media_next_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.media_next_key_code())
            elif event == AdbKeyCodeHandler.media_prev:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.media_previous_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.media_previous_key_code())
            else:
                robot_print_error("%s is not a known event, please configure this event or ask automation framework"
                                  " developer for more help" % event)
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_left_right(self, event: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC key event in given Android ID(which user pass in config file)
        This method send the
            1. Swipe left/ Move left
            2. Swipe right/ Move right
        :param event: (String) event to send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = None
            cmd_release = None
            if event == AdbKeyCodeHandler.left:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.left_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.left_key_code())
            elif event == AdbKeyCodeHandler.right:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.right_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.right_key_code())
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_up_down(self, event: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC  key event in given Android ID(which user pass in config file)
        This method send the
            1. Move UP/ Swipe UP
            2. Move Down/ Swipe Down
        :param event: (String) event to send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = None
            cmd_release = None
            if event == AdbKeyCodeHandler.up:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.up_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.up_key_code())
            elif event == AdbKeyCodeHandler.down:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.down_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.down_key_code())
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_handle_app(self, app: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC  key event in given Android ID(which user pass in config file)
        This method send the
            1. Setting
            2. Call
            3. Media
            4. Source
            5. Favorite
            6. Phone
            7. OK
        :param app: (String) name of app to be send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = None
            cmd_release = None
            if app == AdbKeyCodeHandler.setting:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.setting_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.setting_key_code())
            elif app == AdbKeyCodeHandler.phone:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.phone_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.phone_key_code())
            elif app == AdbKeyCodeHandler.favorite:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.favorite_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.favorite_key_code())

            elif app == AdbKeyCodeHandler.media:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.media_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.media_key_code())

            elif app == AdbKeyCodeHandler.source:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.source_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.source_key_code())
            elif app == AdbKeyCodeHandler.ok:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.ok_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.ok_key_code())
            elif app == AdbKeyCodeHandler.call:
                cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                    keycode=self.config_manger.call_key_code())
                cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                    keycode=self.config_manger.call_key_code())
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_back(self, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC  key event in given Android ID(which user pass in config file)
        This method send the
            1. Back press
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                keycode=self.config_manger.back_key_code())
            cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                keycode=self.config_manger.back_key_code())
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def swc_adb_custom(self, key_code: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the SWC custom key event in given Android ID(which user pass in config file)
        :param key_code: (String) key code to be send
        :param long_press: True is press long otherwise False. Default is False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                keycode=key_code)
            cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                keycode=key_code)
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def adb_custom_key_event(self, key_code: str, long_press: bool = False, duration: float = 0):
        """
        This method is used to send the generic custom key event in given Android ID(which user pass in config file)
        :param key_code: (String) key code to be send
        :param long_press: True if perform long press otherwise False
        :param duration: long press duration in float.
        :return: None
        :except: Handle the Generic exception
        """
        try:
            cmd_press = "input keyevent {keycode}".format(keycode=key_code)
            self.__send_key_code(cmd_press=cmd_press, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error("Error to send the command, EXCEPTION: %s" % exp)
            raise Exception("Error to send the adb command")

    def adb_custom_car_service_key_event(self, key_code: int, long_press: bool = False, duration: float = 0):
        """
        Send the ADB custom Car Service key event
        :param: key_code: Integer value of Key code
        :param: long_press: True if perform long press, Otherwise False
        :param duration: long press duration in float.
        """
        try:
            cmd_press = "dumpsys car_service inject-vhal-event 289475088 0,{keycode},0".format(
                keycode=key_code)
            cmd_release = "dumpsys car_service inject-vhal-event 289475088 1,{keycode},0".format(
                keycode=key_code)
            self.__send_key_code(cmd_press=cmd_press, cmd_release=cmd_release, long_press=long_press, duration=duration)
        except Exception as exp:
            robot_print_error(f"Error to send the customer car service key event, EXCEPTION: {exp}")
