from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.UiTesterClass import UiTesterClass
from ppadb.client import Client as ADBClient
from random import random, seed
import os
from robot.api import logger


class UiTester:
    def __init__(self, hardware_device_id):
        self.UITester = UiTesterClass()
        self.image_path = ""
        self.common_keyword = CommonKeywordsClass()
        client = ADBClient(host='127.0.0.1', port=5037)
        self.device = client.device(hardware_device_id)

    def Compare_Screen(self, ModulePath: str, Image: str, Accuracy: int, TestName: str) -> bool:
        '''
        Compare Complete default screen without modification
        :param ModulePath: Path for res folder
        :param Image: Image name
        :param Accuracy: acurracy factor
        :param TestName: Test name for robot
        :return: Boolean
        '''
        test_case_id = self.common_keyword.get_test_case_id(TestName)
        logger.console(test_case_id)
        directory = self.common_keyword.get_module_folder()
        self.image_path = os.path.join(ModulePath, Image)
        seed(1)
        identifier = int(random() * 10000)
        screenshots_path = os.path.join(directory, "ActualImages", test_case_id + "_" + str(identifier) + ".png")
        self._capture_screenshot(screenshots_path)
        # Log Screenshot
        return self.UITester.compare_default_screen(self.image_path, screenshots_path, Accuracy,
                                                    TestName, str(identifier))

    def Compare_ROI(self, ModulePath: str, Image: str, Coordinates: str, Accuracy: int, TestName: str)-> bool:
        '''
        Compare only particular region of interest of the screen
        :param Coordinates: Coordinates of region of interest
        :param ModulePath: Path for res folder
        :param Image: Image name
        :param Accuracy: acurracy factor
        :param TestName: Test name for robot
        :return: Boolean
        '''
        test_case_id = self.common_keyword.get_test_case_id(TestName)
        directory = self.common_keyword.get_module_folder()
        self.image_path = os.path.join(ModulePath, Image)
        seed(1)
        identifier = int(random() * 10000)
        screenshots_path = os.path.join(directory, "ActualImages", test_case_id + "_" + str(identifier) + ".png")
        self._capture_screenshot(screenshots_path)
        # Log Screenshot
        return self.UITester.compare_region_of_interest(self.image_path, screenshots_path, Coordinates, Accuracy,
                                                        TestName, str(identifier))

    def Compare_Screen_excluding_Dynamic_Regions(self, ModulePath: str, Image: str, Coordinates: str, Accuracy: int, TestName:str)-> bool:
        '''
        Compare only particular region of interest of the screen
        :param Coordinates: Array of Coordinates of dynamic region
        :param ModulePath: Path for res folder
        :param Image: Image name
        :param Accuracy: acurracy factor
        :param TestName: Test name for robot
        :return: Boolean
        '''
        test_case_id = self.common_keyword.get_test_case_id(TestName)
        directory = self.common_keyword.get_module_folder()
        self.image_path = os.path.join(ModulePath, Image)
        seed(1)
        identifier = int(random() * 10000)
        screenshots_path = os.path.join(directory, "ActualImages", test_case_id + "_" + str(identifier) + ".png")
        self._capture_screenshot(screenshots_path)
        # Log Screenshot
        return self.UITester.compare_static_area_multiple(self.image_path, screenshots_path, Coordinates, Accuracy,
                                                          TestName, str(identifier))

    def is_image_displayed_on_screen(self, ModulePath: str, Image: str, TestName: str, Accuracy: int=80) -> int:
        '''
        Verify whether certain image is displayed on screen
        :param ModulePath: Path for res folder
        :param Image:  Image name
        :param Accuracy: acurracy factor (Preffered=80)
        :param TestName: Testcase name Test name for robot
        :return: Boolean
        '''
        test_case_id = self.common_keyword.get_test_case_id(TestName)
        directory = self.common_keyword.get_module_folder()
        self.image_path = os.path.join(ModulePath, Image)
        print(f"Image path: {self.image_path}")
        seed(1)
        identifier = int(random() * 10000)
        screenshots_path = os.path.join(directory, "ActualImages", test_case_id + "_" + str(identifier) + ".png")
        self._capture_screenshot(screenshots_path)
        # Log Screenshot
        coordinates = self.UITester.find_image_in_screen(self.image_path, screenshots_path, Accuracy)
        print(f"Coordinates are: {coordinates}")
        if not coordinates:
            return False
        return True

    def click_on_image(self, action: object, ModulePath: str, Image: str, Accuracy: int, TestName: str):
        '''
        search input imgae and then click on it
        :param action:
        :param ModulePath: Path for res folder
        :param Image:  Image name
        :param Accuracy: acurracy factor (Preffered=80)
        :param TestName: Testcase name Test name for robot
        :return: Array of Coordinates of the image on screen (empty list will be return if image not found)
        '''
        test_case_id = self.common_keyword.get_test_case_id(TestName)
        directory = self.common_keyword.get_module_folder()
        self.image_path = os.path.join(ModulePath, Image)
        seed(1)
        identifier = int(random() * 10000)
        screenshots_path = os.path.join(directory, "ActualImages", test_case_id + "_" + str(identifier) + ".png")
        self._capture_screenshot(screenshots_path)
        # Log Screenshot
        coordinates = self.UITester.find_image_in_screen(self.image_path, screenshots_path, Accuracy)
        print(f"coordinates are: {coordinates}")
        if not coordinates:
            print("Image not Found")
            return False
        center_coordinates = [(coordinates[0][1]+coordinates[1][1])/2, (coordinates[0][0]+coordinates[1][0])/2]
        print(center_coordinates)
        action.tap(x=int(center_coordinates[1]), y=int(center_coordinates[0])).perform()

    def _capture_screenshot(self, path: str):
        '''
        Capture screenshot
        :param path: path where screenshot to be saved
        :return: None
        '''
        try:
            with open(path, "wb") as img_file:
                img_file.write(self.device.screencap())
        except OSError as os_err:
            logger.console("There is an exception to capture screenshot, EXCEPTION: %s" % os_err)
