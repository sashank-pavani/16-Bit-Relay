from Robo_FIT.GenericLibraries.GenericOpLibs.Projection.CP.ConfigurationManager import ConfigurationManager
import os
import time


class CarPlayClass:

    def __init__(self, config_path=""):
        """
        Constructor of CP User Class
        :param config_path: global configuration file path
        """
        self.config_manager = ConfigurationManager(config_path)
        self.asset_path = self.config_manager.get_asset_path()

    def carplay_home(self, driver: object):
        """
        Clicks on Home button on CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_home_button())).click()

        except ValueError:
            print("Driver instance is Null")

    def open_phone_app(self, driver: object):
        """
        Opens Phone Application on CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:

            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_phone_app())).click()
        except ValueError:
            print("Driver instance is Null")

    def open_music(self, driver: object):
        """
        Opens Music Application on CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_music_app())).click()
        except ValueError:
            print("Driver instance is Null")

    def open_maps_app(self, driver: object):
        """
        Opens Map Application on CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_maps_app())).click()
        except ValueError:
            print("Driver instance is Null")

    def open_message_app(self, driver: object):
        """
        Opens Message Application on CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, self.config_manager.get_message_app())).click()
        except ValueError:
            print("Driver instance is Null")

    def exit_app(self, driver: object):
        """
        Exits CP projection screen
        :param driver: webdriver instance
        :return: None
        """
        try:
            while not driver.find_element_by_image("EXIT_APP").is_displayed():
                driver.swipe(0, 0, 0, 0)
            # TODO: Enter appropriate swipe coordinates
            driver.find_element_by_image("EXIT_APP").click()

        except ValueError:
            print("Driver instance is Null")

    def CP_click(self, driver: object, image_path):
        """
        Click operation for Carplay Projection
        :param driver: webdriver instance
        :param image_path: Name of the png image (Media_App.png)
        :return:
        """
        try:
            driver.find_element_by_image(os.path.join(self.asset_path, image_path)).click()
        except ValueError:
            print("Driver Instance is Null")

    def CP_long_press(self, driver: object, action: object, image_path, duration=1000):
        """
        Long press operation for Carplay Projection
        :param action: Touch Action driver instance
        :param touch_driver: Touch Driver instance
        :param duration: duration of long press operation
        :param driver: webdriver instance
        :param image_path: Name of the png image (Media_App.png)
        :return:
        """
        try:
            coordinates = driver.find_element_by_image(os.path.join(self.asset_path, image_path)).location
            time.sleep(2)
            action.long_press(x=int(coordinates['x']), y=int(coordinates['y']), duration=duration).perform()
        except ValueError:
            print("Driver Instance is Null")

    def CP_tap(self, driver: object, action: object, image_path, count=1):
        """
        Tap operation for Carplay projection
        :param driver: Web driver instance
        :param action: TouchAction Driver instance
        :param image_path: Name of the png image (Media_App.png)
        :param count: Number of times tap required
        :return:
        """
        try:
            coordinates = driver.find_element_by_image(os.path.join(self.asset_path, image_path)).location
            time.sleep(2)
            action.tap(x=int(coordinates['x']), y=int(coordinates['y']), count=count).perform()
        except ValueError:
            print("Driver Instance is Null")
