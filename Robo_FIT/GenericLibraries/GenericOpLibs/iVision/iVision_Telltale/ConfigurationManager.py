from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Telltale.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug

class ConfigurationManager:
    def __init__(self):
        self.config_reader = ConfigurationReader.get_config_reader()

    def get_url(self, url_key: str) -> str:
        """
        Retrieves the API URL based on the specified key.
        :param url_key: The key in the JSON file under "IvisionURLs" (e.g., "detect_telltale").
        :return: The URL corresponding to the given key or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string(f"IvisionURLs.{url_key}")
        except Exception as e:
            robot_print_error(f"Error retrieving URL '{url_key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve URL for key '{url_key}'.")

    def get_oem(self) -> str:
        """
        Retrieves the OEM (Original Equipment Manufacturer) from the configuration.
        :return: The OEM value from the JSON or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string("OEM")
        except Exception as e:
            robot_print_error(f"Error retrieving OEM from configuration: {e}", print_in_report=True)
            raise ValueError("Failed to retrieve OEM from configuration.")

    def get_telltale_state_color(self, telltale_name: str, state: str = "ON") -> str:
        """
        Retrieves the color code for a given telltale's state (e.g., "ON" or "OFF").
        :param telltale_name: The name of the telltale as per the JSON configuration (case sensitive).
        :param state: The state to fetch the color for. Default is "ON".
        :return: The color code string (e.g., "#999a92") or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string(f"Telltales.{telltale_name}.{state}")
        except Exception as e:
            robot_print_error(f"Error retrieving color for telltale '{telltale_name}' and state '{state}': {e}",
                              print_in_report=True)
            raise ValueError(f"Failed to retrieve telltale state color for '{telltale_name}' in state '{state}'.")

    def get_roi_url(self, url_key: str) -> str:
        """
        Retrieves the API URL based on the specified key.
        :param url_key: The key in the JSON file under "IvisionURLs" (e.g., "detect_telltale").
        :return: The URL corresponding to the given key or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string(f"IvisionURLs.{url_key}")
        except Exception as e:
            robot_print_error(f"Error retrieving URL '{url_key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve URL for key '{url_key}'.")

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

    def get_roi_parameters(self, key: str) -> str:
        """
        Retrieves specific OCR parameter values from the "OCRParameters" section in the configuration.
        :param key: The specific key under "OCRParameters" (e.g., "bw_threshold").
        :return: The corresponding parameter value.
        """
        try:
            return self.config_reader.read_string(f"Parameters_for_ROI_based_verification.{key}")
        except Exception as e:
            robot_print_error(f"Error retrieving OCR parameter '{key}' from configuration: {e}", print_in_report=True)
            raise ValueError(f"Failed to retrieve OCR parameter '{key}' from configuration.")

