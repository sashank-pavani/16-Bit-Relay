from Robo_FIT.GenericLibraries.GenericOpLibs.Projection.AAP.ConfigurationManager import ConfigurationManager
import os
import time
from appium.webdriver import Remote
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class AndroidAutoClass:

    def __init__(self):
        """
        Constructor of AAP User Class
        :param config_path: global configuration file path
        """
        self.config_manager = ConfigurationManager()
        self.asset_path = self.config_manager.get_asset_path()

    def open_app_by_image(self, driver: Remote, app_name: str):
        """
        This Method used to search image name given in aap_config_file.json in key like for example key "Phone"
        will search for "Phone.png" under Android Auto Image Folder and that same image is available on IFCU Current
        Screen then it will click on it.
        :param driver: webdriver instance
        :param app_name: Application Name you want to open key should be same as per JSON Key value.
        :return : None
        """
        try:
            if app_name.title() not in self.config_manager.get_images_key_list():
                raise Exception(f"Invalid Key {app_name}")
            driver.find_element_by_image(os.path.join(self.asset_path,
                                                      self.config_manager.get_image_name(app_name.title()))).click()
        except Exception as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def exit_app(self, driver: Remote):
        """
        Exits AAP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            while not driver.find_element_by_image(
                    os.path.join(self.asset_path, self.config_manager.get_image_name("Exit"))).is_displayed():
                driver.swipe(0, 0, 0, 0)
            # TODO: Enter appropriate swipe coordinates
            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_image_name("Exit"))).\
                click()
        except ValueError:
            robot_print_error("Driver Instance is Null")

    def AAP_click(self, driver: Remote, image_path):
        """
        Click operation for Android Auto Projection
        :param driver: webdriver instance
        :param image_path: Name of the png image (Media_App.png)
        :return:
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, image_path)).click()
        except ValueError:
            robot_print_error("Driver Instance is Null")

    def AAP_long_press(self, driver: Remote, action: Remote, image_path, duration=1000):
        """
        Long Press operation for Android Auto Projection
        :param action: TouchAction Driver instance
        :param duration: duration of long press operation
        :param driver: webdriver instance
        :param image_path: Name of the png image (Media_App.png)
        :return:
        """
        try:
            coordinates = driver.find_element_by_image(os.path.join(self.asset_path, image_path)).location
            time.sleep(2)
            # TODO: Need to check this implementation
            action.long_press(x=int(coordinates['x']), y=int(coordinates['y']), duration=duration).perform()
        except ValueError:
            robot_print_error("Driver Instance is Null")

    def AAP_tap(self, driver: Remote, action: Remote, image_path, count=1):
        """
        Tap operation for Android Auto projection
        :param driver: Web driver instance
        :param action: TouchAction Driver instance
        :param image_path: Name of the png image (Media_App.png)
        :param count: Number of times tap required
        :return:
        """
        try:
            coordinates = driver.find_element_by_image(os.path.join(self.asset_path, image_path)).location
            time.sleep(2)
            # TODO: Need to check this implementation
            action.tap(x=int(coordinates['x']), y=int(coordinates['y']), count=count).perform()
        except ValueError:
            robot_print_error("Driver Instance is Null")
