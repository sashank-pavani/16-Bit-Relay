from CRE.Libraries.ProjectLibs.cVision.Single_Circular_Gauge.ConfigurationReader import ConfigurationReader

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
        reference_image_path = self.config.read_string(f"{key}.reference_image_path")
        if not reference_image_path:
            raise ValueError(f"Reference image path for '{key}' is not specified in the configuration file.")
        return reference_image_path

    def get_boundary_line_color(self, key: str) -> list:
        """
        Retrieves the boundary line color for the given key from the configuration file.

        :param key: The key representing the boundary line color (e.g., "ref_img_bar1", "ref_img_bar2").
        :return: The boundary line color as a list of three integers [B, G, R].
        """
        # Retrieve the boundary line color from the configuration
        boundary_line_color = self.config.read_list(f"{key}.boundary_line_color")
        if not boundary_line_color or len(boundary_line_color) != 3:
            raise ValueError(f"Boundary line color for '{key}' is not specified correctly in the configuration file.")
        return boundary_line_color
