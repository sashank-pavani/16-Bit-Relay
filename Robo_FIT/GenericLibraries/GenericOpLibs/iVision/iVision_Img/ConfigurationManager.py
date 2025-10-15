from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Img.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug


class ConfigurationManager:
    def __init__(self):
        self.config_reader = ConfigurationReader.get_config_reader()

    def get_ivision_base_folder(self):
        """ This function reads ivision_base_folder from Json"""
        base_folder = self.config_reader.read_string(f"paths.ivision_base_folder")
        if not base_folder:
            raise ValueError(f"ivision_base_folder is not set or is empty.")
        return base_folder

    def get_ivision_image_subfolder(self):
        """ This function reads ivision_image_subfolder from Json"""
        image_subfolder = self.config_reader.read_string(f"paths.ivision_image_subfolder")
        if not image_subfolder:
            raise ValueError(f"ivision_image_subfolder is not set or is empty.")
        return image_subfolder

    def get_ivision_result_subfolder(self):
        """ This function reads ivision_result_subfolder from Json"""
        try:
            result_subfolder = self.config_reader.read_string(f"paths.ivision_result_subfolder")
            if not result_subfolder:
                raise ValueError(f"ivision_result_subfolder is not set or is empty.")
            return result_subfolder
        except Exception as e:
            # You can log the error or handle it as needed
            raise ValueError(f"An error occurred while getting the result subfolder: {str(e)}")

    def get_path(self, path_key: str) -> str:
        """
        Retrieves the path based on the specified key.
        :param path_key: The key in the JSON file under "Paths" (e.g., "excel_file_path").
        :return: The path corresponding to the given key or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string(f"Paths.{path_key}")
        except Exception as e:
            robot_print_error(f"Error retrieving path '{path_key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve path for key '{path_key}'.")

    def get_threshold(self) -> str:
        """
        Retrieves the OEM value from the configuration file.
        :return: The OEM value as a string.
        """
        try:
            return self.config_reader.read_string("Pattern_matching_threshold")
        except Exception as e:
            robot_print_error(f"Error retrieving confidence from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve confidence from configuration.")

    def get_black_bg(self) -> str:
        """
        Retrieves the OEM value from the configuration file.
        :return: The OEM value as a string.
        """
        try:
            return self.config_reader.read_string("Required_black_bg")
        except Exception as e:
            robot_print_error(f"Error retrieving confidence from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve confidence from configuration.")

    def get_flag(self, flag_name: str) -> bool:
        """
        Retrieves a boolean flag from the configuration file.
        :param flag_name: The name of the flag to retrieve.
        :return: The flag value as a boolean.
        """
        try:
            value = self.config_reader.read_string(flag_name).strip().lower()
            return value == "true"
        except Exception as e:
            raise ValueError(f"Failed to retrieve flag '{flag_name}' from configuration: {e}")

    def get_blinking_parameters(self, key: str) -> str:
        """
        Retrieves specific OCR parameter values from the "OCRParameters" section in the configuration.
        :param key: The specific key under "OCRParameters" (e.g., "bw_threshold").
        :return: The corresponding parameter value.
        """
        try:
            return self.config_reader.read_string(f"Blinking_rate_verification_parameters.{key}")
        except Exception as e:
            robot_print_error(f"Error retrieving OCR parameter '{key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve OCR parameter '{key}' from configuration.")

