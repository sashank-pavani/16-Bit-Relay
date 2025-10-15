from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_OCR.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error

class ConfigurationManager:
    def __init__(self):
        """
        Initialize the ConfigurationManager and retrieve parameters using ConfigurationReader.
        """
        self.config_reader = ConfigurationReader.get_config_reader()

    def get_url(self, url_key: str) -> str:
        """
        Retrieves the API URL based on the specified key from the "IvisionURLs" section in the configuration.
        :param url_key: The key in the JSON file under "IvisionURLs" (e.g., "detect_text").
        :return: The URL corresponding to the given key.
        """
        try:
            return self.config_reader.read_string(f"IvisionURLs.{url_key}")
        except Exception as e:
            robot_print_error(f"Error retrieving URL '{url_key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve URL for key '{url_key}'.")

    def get_detections(self) -> list:
        """
        Retrieves the detections list from the configuration file.
        :return: The list of detections.
        """
        try:
            return self.config_reader.read_list("detections")
        except Exception as e:
            robot_print_error(f"Error retrieving detections from configuration: {e}", print_in_report=True)
            raise ValueError("Failed to retrieve detections from configuration.")

    def get_ocr_parameters(self, key: str) -> str:
        """
        Retrieves specific OCR parameter values from the "OCRParameters" section in the configuration.
        :param key: The specific key under "OCRParameters" (e.g., "bw_threshold").
        :return: The corresponding parameter value.
        """
        try:
            return self.config_reader.read_string(f"OCRParameters.{key}")
        except Exception as e:
            robot_print_error(f"Error retrieving OCR parameter '{key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve OCR parameter '{key}' from configuration.")

    def get_oem(self) -> str:
        """
        Retrieves the OEM value from the configuration file.
        :return: The OEM value as a string.
        """
        try:
            return self.config_reader.read_string("OEM")
        except Exception as e:
            robot_print_error(f"Error retrieving OEM from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve OEM from configuration.")

    def get_confidence(self) -> int:
        """
        Retrieves the OEM value from the configuration file.
        :return: The OEM value as a string.
        """
        try:
            return self.config_reader.read_int("confidence")
        except Exception as e:
            robot_print_error(f"Error retrieving confidence from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve confidence from configuration.")
