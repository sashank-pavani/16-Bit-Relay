from typing import List
from CRE.Libraries.ProjectLibs.cVision.ProgressBar.ConfigurationReader import ConfigurationReader

class ConfigurationManager:
    def __init__(self):
        # Initialize the configuration reader
        self.config = ConfigurationReader.get_config_reader()

    def get_reference_image_path(self, key: str) -> str:
        """
        Retrieves the reference image path for the given key from the configuration file.

        :param key: The key representing the reference image path (e.g., "ref_img_bar1", "ref_img_bar2").
        :return: The reference image path as a string.
        """
        # Retrieve the image path from the configuration
        reference_image_path = self.config.read_string(f"{key}.ref_image_path")
        if not reference_image_path:
            raise ValueError(f"Reference image path for '{key}' is not specified in the configuration file.")
        return reference_image_path

    def get_fg_color(self, key: str) -> List[int]:
        """
        Retrieves the foreground color for the given key from the configuration file.

        :param key: The key representing the foreground color (e.g., "ref_img_bar1", "ref_img_bar2").
        :return: The foreground color as a list [R, G, B].
        """
        # Retrieve the foreground color from the configuration
        fg_color = self.config.read_list(f"{key}.fg_color")
        if not fg_color or not isinstance(fg_color, list):
            raise ValueError(f"Foreground color for '{key}' is not specified or not a list in the configuration file.")
        return fg_color

    def get_bg_color(self, key: str) -> List[int]:
        """
        Retrieves the background color for the given key from the configuration file.

        :param key: The key representing the background color (e.g., "ref_img_bar1", "ref_img_bar2").
        :return: The background color as a list [R, G, B].
        """
        # Retrieve the background color from the configuration
        bg_color = self.config.read_list(f"{key}.bg_color")
        if not bg_color or not isinstance(bg_color, list):
            raise ValueError(f"Background color for '{key}' is not specified or not a list in the configuration file.")
        return bg_color
