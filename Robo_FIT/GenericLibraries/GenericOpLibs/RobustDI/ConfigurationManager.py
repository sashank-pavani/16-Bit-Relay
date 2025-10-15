import re
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, CRE_LIBRARIES, \
    CRE_EXTERNAL_FILES, CRE_DB_FILES, CRE_INPUT_FILES, ROBO_CAN_INPUT_FILE_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.RobustDI.ConfiguratorReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ConfigurationManager:
    """
    This class is for CAN->to manage configuration 
    """

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()
        self.config_reader = ConfiguratorReader()

    def get_current_high(self) -> float:
        """
        This method is used to read the bus_type from configuration file
        :return: currentHigh as string
        """
        return self.config_reader.read_float("currentHigh")

    def get_current_low(self) -> float:
        """
        This method is used to read the bus_type from configuration file
        :return: currentLow as string
        """
        return self.config_reader.read_float("currentLow")

    def get_image_screenshot_path(self, file_name: str) -> str:
        """
        This method is used to create an Image file from the name given in configuration file
        : param: file_name
        : return: returns the image folder path in Reports folder
        """

        return os.path.join(self.common_keyword.get_image_screenshot_path(), file_name)

    def get_image_name(self):
        """
        This method is used to read the ImageNameON from configuration file
        :return: ImageNameON as string
        """
        try:
            return self.config_reader.read_string("imageNameOn")
        except TypeError:
            robot_print_error("'ImageNameON' Key not present in robust_config_file.json")

    def get_image_name_off(self):
        """
        This method is used to read the ImageNameOFF from configuration file
        :return: ImageNameOFF as string
        """
        try:
            return self.config_reader.read_string("imageNameOff")
        except TypeError:
            robot_print_error("'ImageNameOFF' Key not present in robust_config_file.json")

    def get_template_image_name(self):
        try:
            return self.config_reader.read_list("croppedImagePath")

        except TypeError:
            robot_print_error("'croppedImagePath' key not present in robust_config_file.json")


