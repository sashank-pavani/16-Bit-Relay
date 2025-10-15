from Robo_FIT.GenericLibraries.GenericOpLibs.cVision.cVisionCamera.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)

class ConfigurationManager:
    def __init__(self):
        self.config = ConfigurationReader.get_config_reader()

    def get_cvision_base_folder(self):
        base_folder = self.config.read_string(f"paths.cvision_base_folder")
        if not base_folder:
            raise ValueError(f"cvision_base_folder is not set or is empty.")
        return base_folder

    def get_cvision_image_subfolder(self):
        image_subfolder = self.config.read_string(f"paths.cvision_image_subfolder")
        if not image_subfolder:
            raise ValueError(f"cvision_image_subfolder is not set or is empty.")
        return image_subfolder

    def get_cvision_result_subfolder(self):
        try:
            result_subfolder = self.config.read_string(f"paths.cvision_result_subfolder")
            if not result_subfolder:
                raise ValueError(f"cvision_result_subfolder is not set or is empty.")
            return result_subfolder
        except Exception as e:
            # You can log the error or handle it as needed
            raise ValueError(f"An error occurred while getting the result subfolder: {str(e)}")
    def get_manual_fps(self):
        try:
            result_subfolder = self.config.read_string(f"manual_fps")
            if not result_subfolder:
                raise ValueError(f"manual_fps is not set or is empty.")
            return result_subfolder
        except Exception as e:
            # You can log the error or handle it as needed
            raise ValueError(f"An error occurred while getting the manual_fps: {str(e)}")
    def get_fps(self):
        try:
            result_subfolder = self.config.read_int(f"fps")
            if not result_subfolder:
                raise ValueError(f"fps is not set or is empty.")
            return result_subfolder
        except Exception as e:
            # You can log the error or handle it as needed
            raise ValueError(f"An error occurred while getting the fps: {str(e)}")

