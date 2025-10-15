import os
import random
import re
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Callable, List, Union
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from importlib_metadata import version
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from Robo_FIT.GenericLibraries.GenericOpLibs.ADBLogger.ADBConnectionFile import ADBConnectionFile
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ID_STRUCTURE, XPATH_STRUCTURE, \
    CLASS_STRUCTURE, JPEG_IMAGE_STRUCTURE, PNG_IMAGE_STRUCTURE, XPATH_STRUCTURE_INDEX, WAIT_TIMEOUT, \
    SEARCH_CONTENT_DESC_XPATH, SEARCH_TEXT_XPATH
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info


class AppiumHandler:
    __driver_instance = None

    def handle_exception(func: Callable):
        """
        This function handle web driver exception as decorator
        :return wrapped function which you have passed in argument.
        """

        def wrap_func(self, *args, **kwargs):
            result = None
            try:
                # calling the function with arguments
                result = func(self, *args, **kwargs)
            except WebDriverException as exp:
                robot_print_error(f"WebDriverException, Error to perform {func.__name__!r}, EXCEPTION:{exp}")
                # handling the exception
                flag = self.handle_appium_error(exp)
                if flag:
                    try:
                        # try one more time to perform the function
                        # Assuming that self.handle_appium_error() will solve the issue.
                        result = func(self, *args, **kwargs)
                    except Exception as exp:
                        robot_print_error(f"Error to perform {func.__name__!r} second time, EXCEPTION:{exp}")
                    finally:
                        robot_print_info(f'Function {func.__name__!r} executed second time', underline=True)
                else:
                    robot_print_error(f"WebDriverException:{exp} Not Possible to Handle,Please Try Manual Way!!")
            except Exception as exp:
                robot_print_error(f"Error to call EXCEPTION:{exp}")
            robot_print_info(f'Function {func.__name__!r} executed', underline=True)
            return result

        return wrap_func

    @staticmethod
    def get_appium_driver(appium_server_url: str,
                          desired_capability: dict,
                          power_cycle_cb: Callable = None) -> 'AppiumHandler':
        """
        This function will provide the singleton instance of AppiumHandler class.

        Usage:
            from Robo_FIT.GenericLibraries.GenericOpLibs.AppiumSession.AppiumHandler import AppiumHandler

            appium_handler = AppiumHandler.get_appium_driver(HARDWARE_URL, des_cap)

        :param appium_server_url: appium server url where appium server is running.
        For project HW user can use "HARDWARE_URL" variable of CRE/Libraries/ProjectKeywords/project_keyword.py file.
        :type appium_server_url: String
        :param desired_capability: Appium Desire capability which use to make a connection with Appium server.
        For more please check https://appium.io/docs/en/writing-running-appium/caps/
        :type desired_capability: Dict
        :param power_cycle_cb: Callable function of power mode cycle.
        This function is required if appium server crash or server side issue. We need to restart the appium connection
        and board attached to the system. Every project have their own power boot up sequence. So, please provide that
        function to this class.
        :type power_cycle_cb: Callable
        :return: AppiumHandler class object
        """
        if AppiumHandler.__driver_instance is None:
            AppiumHandler(appium_server_url, desired_capability, power_cycle_cb)
        return AppiumHandler.__driver_instance

    def __init__(self, hw_url: str, desired_capability: dict, power_cycle_cb: Callable = None):
        """
        This is Constructor for Appium Handler Class.
        driver , touch action initialized here and handled web driver exceptions
        :param hw_url: appium server url where appium server is running.
        For project HW user can use "HARDWARE_URL" variable of CRE/Libraries/ProjectKeywords/project_keyword.py file.
        :type hw_url: String
        :param desired_capability: Appium Desire capability which use to make a connection with Appium server.
        For more please check https://appium.io/docs/en/writing-running-appium/caps/
        :type desired_capability: Dict
        :param power_cycle_cb: Callable function of power mode cycle.
        This function is required if appium server crash or server side issue. We need to restart the appium connection
        and board attached to the system. Every project have their own power boot up sequence. So, please provide that
        function to this class.
        :type power_cycle_cb: Callable
        :return: AppiumHandler class object
        """
        try:
            if AppiumHandler.__driver_instance is not None:
                raise Exception("You need to user the HardwareRecoverClass() to "
                                "initialize the HardwareRecoverClass() class.")
            else:
                self.hw_url = hw_url
                self.power_cycle_cb = power_cycle_cb
                self.desire_cap = desired_capability
                self.desire_cap = self.desire_cap
                AppiumHandler.__power_cycle_cb = self.power_cycle_cb
                for i in range(0, 3):
                    try:
                        robot_print_debug(f"Creating Driver instance for des_cap: {desired_capability}")
                        if hw_url is not None and desired_capability is not None:
                            self.driver = webdriver.Remote(hw_url, desired_capabilities=desired_capability)
                            if int(version('Appium-Python-Client').split(".")[0]) < 2 and int():
                                self.action = TouchAction(self.driver)
                            else:
                                self.action = ActionChains(self.driver)
                            self.driver = self.driver
                            AppiumHandler.__action = self.action
                            AppiumHandler.__driver_instance = self
                            break
                        else:
                            raise Exception("Either desired_capability or/and hw_url is equal None")
                    except WebDriverException as web_exp:
                        robot_print_error(
                            f"WebDriverException to send the desire cap : {desired_capability} , EXCEPTION: {web_exp}")
                        self.handle_appium_error(web_exp.msg)
                    except Exception as exp:
                        robot_print_error(f"Error to send the desire cap : {desired_capability} , EXCEPTION: {exp}")
                        self.handle_appium_error(exp)
        except Exception as exp:
            robot_print_error(f"Error to initialize the class {__name__}, EXCEPTION: {exp}")

    @property
    def get_hw_driver(self) -> Union[webdriver.Remote, None]:
        """
        return self.driver instance if it is not None
        """
        return self.driver if self.driver is not None else None

    @property
    def get_hw_action(self) -> Union[TouchAction, None]:
        """
        return self.action instance if it is not None
        """
        return self.action if self.action is not None else None

    @property
    def desire_capability(self) -> dict:
        """
        return desired_capability instance if it is not None
        """
        return self.desire_cap

    @desire_capability.setter
    def desire_capability(self, des_cap: dict):
        """
        desire_cap value updating with value global desired_capability
        """
        self.desire_cap = des_cap

    def kill_system_port(self):
        """
        This function is used to kill the exiting system port
        :return: None
        """
        try:
            status = subprocess.Popen("netstat -ano", shell=True, stdout=subprocess.PIPE)
            net_data, err = status.communicate()
            net_data = net_data.decode('utf-8')
            robot_print_info(f"Netstat output: {net_data}")
            pids = re.findall(f"127.0.0.1:82.*", net_data.strip())
            killed_pid = 0
            for pid in pids:
                if pid.split()[-2] == "LISTENING":
                    kill_pid = pid.split()[-1]
                    if kill_pid != killed_pid:
                        killed_pid = kill_pid
                        robot_print_debug(f"Killing PID: {kill_pid}", print_in_report=True)
                        status = subprocess.Popen(f"taskkill /PID {kill_pid} /F", shell=True, stdout=subprocess.PIPE)
                        robot_print_info(f"Kill status: {status.communicate()}")
            # pid = (re.search(f"127.0.0.1:{desired_capability['systemPort']}.*", net_data.strip()))[0].split()[-1]
        except Exception as exp:
            robot_print_error(
                f"Error to kill system port : {self.desire_cap['systemPort']}, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def uninstall_uiautomator_app(self, hw_id: str = None):
        """
        This function is used to uninstall the appium application form the target side.

        For example:
            adb -s 18211JEC206674 uninstall io.appium.settings
            adb -s 18211JEC206674 uninstall io.appium.uiautomator2.server.test
            adb -s 18211JEC206674 uninstall io.appium.uiautomator2.server

        :param hw_id: Target device ID.
        :return: None
        :raise ValueError: Raise ValueError if Hw_id is not a valid ID.
        """
        try:
            if hw_id is None:
                raise ValueError("hw_id should be string value can't be None")
            status = subprocess.Popen(f"adb -s {hw_id} uninstall io.appium.settings", shell=True,
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            robot_print_info(f"uninstall io.appium.settings STATUS:{status.communicate()}")
            status = subprocess.Popen(
                f"adb -s {hw_id} uninstall io.appium.uiautomator2.server.test", shell=True,
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            robot_print_info(f"uninstall io.appium.uiautomator2.server.test STATUS:{status.communicate()}")
            status = subprocess.Popen(f"adb -s {hw_id} uninstall io.appium.uiautomator2.server",
                                      shell=True,
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            robot_print_info(f"uninstall io.appium.uiautomator2.server STATUS:{status.communicate()}")
        except Exception as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def handle_appium_error(self, exp):
        """
        This function is used to handle the Appium errors.
        :param exp: Appium error.
        :return: None
        """
        if "socket hang up" in str(exp):
            robot_print_debug(f"Handling 'socket hang up' error", True)
            self.kill_system_port()
            self.desire_cap['systemPort'] = random.randrange(8200, 8210, 1)
            robot_print_debug(f"New System Port Assigned:{self.desire_cap['systemPort']}")
            self.restart_web_driver()
            return True
        if "ECONNREFUSED" in str(exp):
            robot_print_debug(f"Handling 'ECONNREFUSED' error", True)
            self.kill_system_port()
            self.desire_cap['systemPort'] = random.randrange(8200, 8210, 1)
            robot_print_debug(f"New System Port Assigned:{self.desire_cap['systemPort']}")
            self.restart_web_driver()
            return True
        if "uiautomator2ServerLaunchTimeout" in str(exp):
            robot_print_debug(f"Handling 'uiautomator2ServerLaunchTimeout' error", True)
            self.desire_cap["uiautomator2ServerLaunchTimeout"] = self.desire_cap[
                                                                     "uiautomator2ServerLaunchTimeout"] + \
                                                                 10000 if \
                "uiautomator2ServerLaunchTimeout" in self.desire_cap.keys() else 50000
            return True
        if "SessionNotCreatedException" in str(exp):
            robot_print_debug(f"Handling 'SessionNotCreatedException' error", True)
            self.power_cycle_cb()
            self.restart_web_driver()
            return True
        if "IllegalStateException" in str(exp):
            robot_print_debug(f"Handling 'IllegalStateException' error", True)
            self.uninstall_uiautomator_app()
            # Try to uninstall the appium apk from HW and install again by restart the webdriver
            return True
        if "A session is either terminated or not started" in str(exp):
            robot_print_debug(f"Handling 'A session is either terminated or not started' error", True)
            # self.driver.start_session(self.desire_cap)
            self.restart_web_driver()
            return True
        if "uiautomator2ServerInstallTimeout" in str(exp):
            robot_print_debug(f"Handling 'uiautomator2ServerInstallTimeout' error", True)
            self.desire_cap.update({"appWaitForLaunch": False})
            self.driver.start_session(self.desire_cap)
            return True
        return False

    def restart_web_driver(self) -> bool:
        """
        Restart Web Driver Function Reset Driver and again Start Driver Session and here also handled
        Web Driver Exceptions
        :return: True if restarted successfully, Otherwise False
        :rtype: Boolean
        """
        try:
            count = 0
            adb_connection = ADBConnectionFile()
            while count <= 3:
                try:
                    device_status = adb_connection.get_adb_device_status(
                        self.desire_cap["deviceName"])
                    if device_status == "offline":
                        robot_print_info(
                            f"Device not online can't re-start the web driver, DEVICE_STATUS={device_status}")
                        count = 3
                        return False
                    else:
                        robot_print_debug(f"Driver:{self.driver}", True)
                        robot_print_info(f"After Restart Web-Driver DEVICE_STATUS={device_status}")
                        try:
                            self.driver.start_session(self.desire_cap)
                            count = 3
                            return True
                        except WebDriverException as web_exp:
                            robot_print_debug(f"reset session thrown EXCEPTION:{web_exp}", True)
                            # AppiumHandler.handle_appium_error(web_exp.msg)
                            count += 1
                except Exception as exp:
                    robot_print_error(f"EXCEPTION:{exp}")
                    # AppiumHandler.handle_appium_error(exp)
                    count += 1
            else:
                Exception(f"Driver status:{self.driver} and count:{count}")
        except Exception as exp:
            robot_print_error(f"EXCEPTION:{exp}")
            return False

    def __find_element_v3_plus(self, locator: str, is_elements: bool = False) -> Union[WebElement, List[WebElement]]:
        """
        This function is used to find the element base on the locator provided by the user.

        **Appium-Python-Client version should be <= 1.3.0**

        :param locator: Locator of the element. It can be ID, XPATH, CLASS NAME, IMAGE etc.
        :return: selenium.webdriver.remote.webelement.WebElement object or WebElements
       """
        try:
            if len(locator) == 0:
                raise ValueError("Element locator '" + locator + "' did not match size.")
            else:
                if locator.startswith(XPATH_STRUCTURE) or locator.startswith(XPATH_STRUCTURE_INDEX):
                    if not is_elements:
                        return self.driver.find_element_by_xpath(locator)
                    else:
                        return self.driver.find_elements_by_xpath(locator)
                elif ID_STRUCTURE in locator:
                    if not is_elements:
                        return self.driver.find_element_by_id(locator)
                    else:
                        return self.driver.find_elements_by_id(locator)
                elif CLASS_STRUCTURE in locator:
                    if not is_elements:
                        return self.driver.find_element_by_class_name(locator)
                    else:
                        return self.driver.find_elements_by_class_name(locator)
                elif locator.endswith(PNG_IMAGE_STRUCTURE) or locator.endswith(JPEG_IMAGE_STRUCTURE):
                    if not is_elements:
                        return self.driver.find_element_by_image(locator)
                    else:
                        return self.driver.find_elements_by_image(locator)
                else:
                    raise ValueError("Element locator '" + locator + "' did not match any elements.")
        except NoSuchElementException as exp:
            robot_print_error(f"Element {locator} did not match any elements  EXCEPTION:{exp}")

    def __find_element_v4_plus(self, locator: str, is_elements: bool = False) -> Union[WebElement, List[WebElement]]:
        """
        This function is used to find the element base on the locator provided by the user.

        **Appium-Python-Client version should be >= 2.7.1**

        :param locator: Locator of the element. It can be ID, XPATH, CLASS NAME, IMAGE etc.
        :return: selenium.webdriver.remote.webelement.WebElement object or WebElements
        """
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            if len(locator) == 0:
                raise ValueError("Element locator '" + locator + "' did not match size.")
            else:
                if locator.startswith(XPATH_STRUCTURE) or locator.startswith(XPATH_STRUCTURE_INDEX):
                    if not is_elements:
                        return self.driver.find_element(AppiumBy.XPATH, locator)
                    else:
                        return self.driver.find_elements(AppiumBy.XPATH, locator)
                elif ID_STRUCTURE in locator:
                    if not is_elements:
                        return self.driver.find_element(AppiumBy.ID, locator)

                    else:
                        return self.driver.find_elements(AppiumBy.ID, locator)
                elif CLASS_STRUCTURE in locator:
                    if not is_elements:
                        return self.driver.find_element(AppiumBy.CLASS_NAME, locator)
                    else:
                        return self.driver.find_elements(AppiumBy.CLASS_NAME, locator)
                elif locator.endswith(PNG_IMAGE_STRUCTURE) or locator.endswith(JPEG_IMAGE_STRUCTURE):
                    if not is_elements:
                        return self.driver.find_element(AppiumBy.IMAGE, locator)
                    else:
                        return self.driver.find_elements(AppiumBy.IMAGE, locator)
                else:
                    raise ValueError("Element locator '" + locator + "' did not match any elements.")
        except ImportError as imp_err:
            robot_print_error(f"Error to import the AppiumBy class. Appium-Python-Client version should be >= 2.7.1, "
                              f"EXCEPTION: {imp_err}")

    @handle_exception
    def find_element(self, locator: str) -> WebElement:
        """
        This function is used to find the element base on the locator provided by the user.
        :param locator: Locator of the element. It can be ID, XPATH, CLASS NAME, IMAGE etc.
        :return: selenium.webdriver.remote.webelement.WebElement object
        """
        if int(version('selenium').split(".")[0]) < 4 and int(version('Appium-Python-Client').split(".")[0]) < 2:
            return self.__find_element_v3_plus(locator)
        elif int(version('selenium').split(".")[0]) >= 4 and int(version('Appium-Python-Client').split(".")[0]) >= 2:
            return self.__find_element_v4_plus(locator)

    @handle_exception
    def find_elements(self, locator: str) -> Union[WebElement, List[WebElement]]:
        """
        This function will find the elements and return to the user.
        :param locator: Locator which need to be found.
        :return: List of all the available WebElements for given locator.
        :raise ValueError: If locator is not a valid locator it will raise ValueError
        """
        if int(version('selenium').split(".")[0]) < 4 and float(version('Appium-Python-Client').split(".")[0]) < 2:
            return self.__find_element_v3_plus(locator, is_elements=True)
        elif int(version('selenium').split(".")[0]) >= 4 and float(
                version('Appium-Python-Client').split(".")[0]) >= 2:
            return self.__find_element_v4_plus(locator, is_elements=True)

    @handle_exception
    def get_element_text(self, locator: Union[str, WebElement]) -> str:
        """
        This function will return the text of the locator.
        :param locator: Locator value
        :return: String value of the locator Text
        """
        try:
            if isinstance(locator, WebElement):
                return locator.text
            else:
                element = self.find_element(locator)
                robot_print_debug(f"Got Text:{element.text}", True)

                return element.text
        except ValueError as exp:
            robot_print_error(f"{locator} dose not have text value EXCEPTION:{exp}")

    @handle_exception
    def click_element(self, locator: Union[str, WebElement]):
        """
        Click on the give locator. If locator "clickable" property is "False" then
        it will not be able to click on that element
        :param locator: Locator which need to be clicked
        :return: None
        """
        try:
            if isinstance(locator, WebElement):
                self.wait_until_element_present(locator)
                locator.click()
                return True
            else:
                self.wait_until_element_present(locator)
                element = self.find_element(locator)
                element.click()
                return True
            # robot_print_debug(f"<element text:{self.get_element_text(element)}> Clicked on Element:{locator}", True)
        except ValueError as exp:
            robot_print_error(f"It seems locator: {locator} is not a valid locator, Please check the value,"
                              f" EXCEPTION:{exp}")
            return False

    @handle_exception
    def get_current_packages(self) -> str:
        """
        This function will provide the current package name which will be display on the screen currently
        when function called.
        :return: String value of the package
        """
        return self.driver.current_package

    @handle_exception
    def double_click_element(self, locator: str):
        """
        Double-click on the give locator.
        :param locator: Locator to be clicked
        :return: None
        """
        action_chain = ActionChains(self.driver)
        action_chain.move_to_element(locator).double_click(locator).perform()

    @handle_exception
    def is_enabled(self, locator: Union[str, WebElement]) -> bool:
        """
        Returns whether the element is enabled.
        :param locator: Locator is enabled
        :return: True if locator found and enabled else False.
        """
        if isinstance(locator, WebElement):
            return locator.is_enabled()
        else:
            return self.find_element(locator).is_enabled()

    @handle_exception
    def is_selected(self, locator: Union[str, WebElement]) -> bool:
        """
        Returns whether the element is selected.
        :param locator: Locator is selected
        :return: True if locator found and selected else False.
        """
        if isinstance(locator, WebElement):
            return locator.is_selected()
        else:
            return self.find_element(locator).is_selected()

    @handle_exception
    def is_displayed(self, locator: Union[str, WebElement]) -> bool:
        """
        Returns whether the element is displayed on screen.
        :param locator: Locator is displayed
        :return: True if locator displayed else False.
        """
        if isinstance(locator, WebElement):
            return locator.is_displayed()
        else:
            return self.find_element(locator).is_displayed()

    @handle_exception
    def is_keyboard_visible(self):
        """
        If Keyboard displayed on current screen it returns True else False
        """
        return self.driver.is_keyboard_shown()

    @handle_exception
    def get_size(self, locator: Union[str, WebElement]) -> dict:
        """This Function Returns locator size as format dict format
        :return : {"height": size["height"],"width": size["width"]}"""
        if isinstance(locator, WebElement):
            return locator.size
        else:
            return self.driver.find_element(locator).size

    @handle_exception
    def clear_entered_text(self, locator: Union[str, WebElement]):
        """
        Clears the user entered text in EDIT Text Filed.
        :param locator: Locator where user entered text.
        :return: None
        """
        if isinstance(locator, WebElement):
            return locator.clear()
        else:
            return self.driver.find_element(locator).clear()

    @handle_exception
    def wait_until_activity_launch(self, activity, timeout: int = 30) -> bool:
        """
        Wait until current activity and given activity match till timeout given.
        if current activity and given activity not matched after some time it will return true else False with error
        message.
        :param activity: expected activity
        :param timeout:  max time wait till activity matches.
        :return: True if Activity match with in timeout time else False
        """
        end_time = datetime.now() + timedelta(seconds=timeout)
        while end_time >= datetime.now():
            current_activity = self.driver.current_activity
            if activity == current_activity:
                return True
        else:
            robot_print_error(f"{self.driver.current_activity}!={activity} after {timeout} Timeout")
            return False

    @handle_exception
    def click_by_content_desc(self, content_string: str) -> bool:
        """
        This Function check content-desc if present in page it will click that.
        :param content_string: content-desc element attribute
        :return: True if element clicked successfully else False.
        """
        self.wait_until_element_present(SEARCH_CONTENT_DESC_XPATH.format(content_string))
        return self.click_element(SEARCH_CONTENT_DESC_XPATH.format(content_string))

    @handle_exception
    def click_by_text(self, search_text: str) -> bool:
        """
        This Function check text if present in page it will click that.
        :param search_text: text element attribute
        :return: True if element clicked successfully else False.
        """
        self.wait_until_element_present(SEARCH_TEXT_XPATH.format(search_text))
        return self.click_element(SEARCH_TEXT_XPATH.format(search_text))

    def __verify_element_type(self, locator_or_text: Union[str, WebElement], is_text: bool):
        """
        based on locator type tuple of locator format will be return
        :param locator_or_text: should be ID,XPATH,CLASS Element else it will raise ValueError for that
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                should be type of ID, CLASS, XPATH
        :raise : Value Error
        """
        if is_text:
            if locator_or_text.startswith(XPATH_STRUCTURE) or locator_or_text.startswith(XPATH_STRUCTURE_INDEX) or \
                    ID_STRUCTURE in locator_or_text or CLASS_STRUCTURE in locator_or_text:
                raise ValueError(f"is_text={is_text} then locator should not be ID,XPATH,CLASS Type WebElement!")
        else:
            if not (locator_or_text.startswith(XPATH_STRUCTURE) or locator_or_text.startswith(
                    XPATH_STRUCTURE_INDEX) or ID_STRUCTURE in locator_or_text or CLASS_STRUCTURE in locator_or_text):
                raise ValueError(f"is_text={is_text} then locator should be ID,XPATH,CLASS Type WebElement!")

    def __get_element(self, locator_or_text: Union[str, WebElement]) -> tuple:
        """
        based on locator type tuple of locator format will be return
        :param locator_or_text: Web element or text
        """
        if locator_or_text.startswith(XPATH_STRUCTURE) or locator_or_text.startswith(XPATH_STRUCTURE):
            locator_or_text = (By.XPATH, locator_or_text)
        elif ID_STRUCTURE in locator_or_text:
            locator_or_text = (By.ID, locator_or_text)
        elif CLASS_STRUCTURE in locator_or_text:
            locator_or_text = (By.CLASS_NAME, locator_or_text)
        return locator_or_text

    @handle_exception
    def wait_until_element_present(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                   time_out: int = WAIT_TIMEOUT) -> WebElement:
        """
        An expectation for checking that an element is present on the DOM
        of a page. This does not necessarily mean that the element is visible.
        :param time_out: time to wait
        :param locator_or_text: used to find the element ID,XPATH,CLASS_NAME
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                        should be type of ID, CLASS, XPATH
        :return: the WebElement once it is located
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Present in DOM within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=True)
            locator_or_text = self.__get_element(locator_or_text)
            wait.until(ec.presence_of_element_located(locator_or_text), message=message)
        else:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.presence_of_element_located(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.presence_of_element_located(locator_or_text), message=message)

    @handle_exception
    def wait_until_elements_present(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                    time_out: int = WAIT_TIMEOUT) -> Union[WebElement, List[WebElement]]:
        """
        An expectation for checking that an element is present on the DOM
        of a page. This does not necessarily mean that the element is visible.
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                        should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :param locator_or_text: used to find the element ID,XPATH,CLASS_NAME. provide find elements locator here.
        :return: the WebElement once it is located
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Present in DOM within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            wait.until(ec.presence_of_all_elements_located(locator_or_text), message=message)
        else:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.presence_of_all_elements_located(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.presence_of_all_elements_located(locator_or_text), message=message)

    @handle_exception
    def wait_until_element_visible(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                   time_out: int = WAIT_TIMEOUT) -> WebElement:
        """
        An expectation for checking that an element is present on the DOM of a
        page and visible. Visibility means that the element is not only displayed
        but also has a height and width that is greater than 0.
        :param locator_or_text: used to find the element. provide find element locator here.
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                        should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :return: WebElement once it is located and visible
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Visible in DOM within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            wait.until(ec.visibility_of_element_located(locator_or_text), message=message)
        else:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_element_located(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_element_located(locator_or_text))

    @handle_exception
    def wait_until_elements_visible(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                    time_out: int = WAIT_TIMEOUT) -> Union[WebElement, List[WebElement]]:
        """
        An expectation for checking that there is at least one element visible
        on a web page.
        :param locator_or_text: used to find the element. provide find elements locator here.
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :return: the list of WebElements once they are located.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Visible in DOM within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            return wait.until(ec.visibility_of_all_elements_located(locator_or_text), message=message)
        else:
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_all_elements_located(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_all_elements_located(locator_or_text), message=message)

    @handle_exception
    def wait_until_at_least_one_element_visible(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                                time_out: int = WAIT_TIMEOUT) -> WebElement:
        """
        An expectation for checking that there is at least one element visible
        on a web page.
        :param locator_or_text: used to find the element. provide find elements locator here.
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :return: the list of WebElements once they are located.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Visible in DOM within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            return wait.until(ec.visibility_of_any_elements_located(locator_or_text), message=message)
        else:
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_any_elements_located(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.visibility_of_any_elements_located(locator_or_text), message=message)

    @handle_exception
    def wait_until_element_clickable(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                     time_out: int = WAIT_TIMEOUT) -> bool:
        """
        An Expectation for checking an element is visible and enabled such that
        you can click it.
        :param locator_or_text: element is either a locator (text) or an WebElement. provide find elements locator here.
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                        should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :return: True  if clickable else False.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Clickable within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            return wait.until(ec.element_to_be_clickable(locator_or_text), message=message)
        else:
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.element_to_be_clickable(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.element_to_be_clickable(locator_or_text), message=message)

    @handle_exception
    def wait_until_element_selection_state(self, locator_or_text: Union[str, WebElement], is_selected: bool = True,
                                           is_text: bool = False, time_out: int = WAIT_TIMEOUT) -> bool:
        """
        An expectation to locate an element and check if the selection state
        specified is in that state.
        :param is_selected: is_selected is a boolean
        :param locator_or_text: is a tuple of (by, path)
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                        should be type of ID, CLASS, XPATH
        :param time_out: time to wait
        :return: True  if clickable else False.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Selected within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            return wait.until(
                ec.element_located_selection_state_to_be(locator_or_text, is_selected=is_selected), message=message)
        else:
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.element_located_selection_state_to_be(locator_or_text, is_selected=is_selected),
                                  message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.element_located_selection_state_to_be(locator_or_text, is_selected=is_selected),
                                  message=message)

    @handle_exception
    def wait_until_element_invisible(self, locator_or_text: Union[str, WebElement],
                                     time_out: int = WAIT_TIMEOUT) -> bool:
        """
        An Expectation for checking that an element is either invisible or not
        present on the DOM.
        :param locator_or_text: element is either a locator (text) or an WebElement
        :param time_out: time to wait
        :return: True  if clickable else False.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} Not Invisible(Present) on page within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        locator_or_text = self.__get_element(locator_or_text)
        return wait.until(ec.invisibility_of_element(locator_or_text), message=message)

    @handle_exception
    def wait_until_text_present_in_element(self, locator_or_text: Union[str, WebElement], expected_text: str,
                                           time_out: int = WAIT_TIMEOUT) -> bool:
        """
        An expectation for checking if the given text is present in the specified element.
        :param expected_text:  expected text you want to search in locator like ID, CLASS, XPATH
        :param locator_or_text: element is either a locator (text) or an WebElement
        :param time_out: time to wait
        :return: True  if clickable else False.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Text={expected_text} not present in Locator={locator_or_text} within given timeout " \
                  f"{WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        locator_or_text = self.__get_element(locator_or_text)
        return wait.until(ec.text_to_be_present_in_element(locator_or_text, expected_text), message=message)

    @handle_exception
    def wait_until_element_staleness(self, locator_or_text: Union[str, WebElement], is_text: bool = False,
                                     time_out: int = WAIT_TIMEOUT) -> bool:
        """
        Wait until an element is no longer attached to the DOM.
        :param locator_or_text: is the element to wait for. locator=self.find_element(element)
        :param time_out: time to wait
        :param is_text: if this is true means locator should be type of expected text you want to search else it
                should be type of ID, CLASS, XPATH
        :return:  returns False if the element is still attached to the DOM, true otherwise.
        Example use:
        def wait_for_element_not_present(self, element, timeout):\
            found_element = None
            try:
                found_element = self.find(element, timeout=0)
            except ElementNotFound:
                pass
            if found_element:
                wait = WebDriverWait(self, timeout)
                message = ('Timeout waiting for element {} to not be present'
                           .format(found_element.name))
                wait.until(ec.staleness_of(found_element), message=message)
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Locator={locator_or_text} is enabled(is stale) within given timeout {WAIT_TIMEOUT}"
        if len(locator_or_text) == 0:
            raise ValueError("Element locator '" + locator_or_text + "' did not match size.")
        if not is_text:
            self.__verify_element_type(locator_or_text, is_text=is_text)
            locator_or_text = self.__get_element(locator_or_text)
            return wait.until(ec.staleness_of(locator_or_text), message=message)
        else:
            try:
                locator_or_text = (By.XPATH, SEARCH_TEXT_XPATH.format(locator_or_text))
                return wait.until(ec.staleness_of(locator_or_text), message=message)
            except Exception:
                locator_or_text = (By.XPATH, SEARCH_CONTENT_DESC_XPATH.format(locator_or_text))
                return wait.until(ec.staleness_of(locator_or_text), message=message)

    @handle_exception
    def wait_until_alert_present(self, time_out: int = WAIT_TIMEOUT) -> bool:
        """
        An expectation for checking if the given text is present in the specified element.
        :param time_out: time to wait
        :return: True  if alert present in page else False.
        """
        wait = WebDriverWait(self.driver, time_out)
        message = f"Alert not present within given timeout {WAIT_TIMEOUT}"
        return wait.until(ec.alert_is_present(), message=message)
