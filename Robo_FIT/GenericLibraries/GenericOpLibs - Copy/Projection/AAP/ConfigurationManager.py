from Robo_FIT.GenericLibraries.GenericOpLibs.Projection.AAP.ConfigurationReader import ConfiguratorReader


class ConfigurationManager:

    def __init__(self):
        """
        Constructor of ConfigurationManager
        :param config_path: global file configuration path and parameter passed by UserAAP class
        """
        self.config_file = ConfiguratorReader()
        self.json_path = self.config_file.config_path

    def get_asset_path(self):
        return self.config_file.read_string("DeviceAssetPath")

    def get_images_dict(self) -> dict:
        return self.config_file.read_configuration(self.json_path)

    def get_images_key_list(self) -> list:
        return list(self.config_file.read_configuration(self.json_path).keys())[1:]

    def get_image_name(self, key: str) -> str:
        return self.config_file.read_string(key)
