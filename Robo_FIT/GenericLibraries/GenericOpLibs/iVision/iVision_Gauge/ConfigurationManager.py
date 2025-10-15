from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Gauge.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *


class ConfigurationManager:
    def __init__(self):
        self.config_reader = ConfigurationReader.get_config_reader()

    def get_url(self, url_key: str) -> str:
        """
        Retrieves the API URL based on the specified key.
        :param url_key: The key in the JSON file (e.g., "detect_gauges_generalised").
        :return: The URL corresponding to the given key or raises an exception if not found.
        """
        try:
            return self.config_reader.read_string(f"IvisionURLs.{url_key}")  # Access URL based on the key
        except Exception as e:
            robot_print_error(
                f"Error retrieving '{url_key}' from configuration: {e}", print_in_report=True
            )
            raise ValueError(f"Failed to retrieve URL for key '{url_key}'")

    def get_oem(self) -> str:
        """
        Retrieves the OEM name from the configuration.
        :return: The OEM value from the JSON.
        """
        try:
            oem = self.config_reader.read_string("OEM")  # Use key to get the OEM string (e.g., "GM")
            robot_print_debug(f"Using OEM: {oem}")
            return oem
        except Exception as e:
            robot_print_error(f"Error retrieving OEM: {e}")
            raise ValueError(f"Failed to retrieve OEM from configuration: {e}")

    def get_gauge_shape(self, gauge_type: str) -> str:
        """
        Retrieves the gauge shape for a specific gauge type based on JSON configuration.
        :param gauge_type: The type of gauge (e.g., "FUELLEVEL").
        :return: The shape of the gauge (e.g., "CIRCLE_GAUGE") or "Unknown" if not found.
        """
        try:
            # Fetch the list of gauges from the JSON
            gauges = self.config_reader.read_list("Gauges")
            robot_print_debug(f"Retrieved Gauges: {gauges}")

            # Validate Gauges list
            if not gauges or not isinstance(gauges, list):
                raise ValueError("Gauges list is empty or invalid.")

            # Search for the specified gauge type and return the shape
            for gauge in gauges:
                if gauge.get("Gauge_type") == gauge_type:
                    return gauge.get("Gauge_shape", "Unknown")  # Default "Unknown" if not found

            # If no match is found
            raise ValueError(f"Gauge type '{gauge_type}' not found in the configuration.")
        except KeyError as ke:
            raise ValueError(f"Invalid key in JSON: {ke}")
        except Exception as e:
            raise ValueError(f"Unexpected error retrieving gauge shape: {e}")

    def get_min_value(self, gauge_type: str) -> int:
        """
        Retrieves the minimum value for a specific gauge type.
        :param gauge_type: The type of gauge (e.g., "FUELLEVEL").
        :return: The minimum value for the gauge or -1 if not found.
        """
        try:
            gauges = self.config_reader.read_list("Gauges")
            robot_print_debug(f"Retrieved Gauges: {gauges}")

            if not gauges or not isinstance(gauges, list):
                raise ValueError("Gauges list is empty or invalid.")

            for gauge in gauges:
                if gauge.get("Gauge_type") == gauge_type:
                    return gauge.get("Min_value", -1)
            raise ValueError(f"Gauge type '{gauge_type}' not found in the configuration.")
        except Exception as e:
            robot_print_error(f"Unexpected error retrieving min value: {e}")
            raise ValueError(f"Unexpected error retrieving min value: {e}")

    def get_max_value(self, gauge_type: str) -> int:
        """
        Retrieves the maximum value for a specific gauge type.
        :param gauge_type: The type of gauge (e.g., "FUELLEVEL").
        :return: The maximum value for the gauge or -1 if not found.
        """
        try:
            gauges = self.config_reader.read_list("Gauges")
            robot_print_debug(f"Retrieved Gauges: {gauges}")

            if not gauges or not isinstance(gauges, list):
                raise ValueError("Gauges list is empty or invalid.")

            for gauge in gauges:
                if gauge.get("Gauge_type") == gauge_type:
                    return gauge.get("Max_value", -1)

            raise ValueError(f"Gauge type '{gauge_type}' not found in the configuration.")
        except KeyError as ke:
            raise ValueError(f"Invalid key in JSON: {ke}")
        except Exception as e:
            raise ValueError(f"Unexpected error retrieving max value: {e}")