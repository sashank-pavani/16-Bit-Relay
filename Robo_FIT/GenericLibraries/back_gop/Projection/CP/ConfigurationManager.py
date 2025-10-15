from Robo_FIT.GenericLibraries.GenericOpLibs.Projection.CP.ConfigurationReader import ConfiguratorReader


class ConfigurationManager:

    def __init__(self, config_path):
        """
        Constructor of ConfigurationManager
        :param config_path: global file configuration path and parameter passed by UserCP class
        """
        self.config_file = ConfiguratorReader()

    def get_asset_path(self):
        return self.config_file.read_string('DeviceAssetPath')

    def get_home_button(self):
        return self.config_file.read_string("Home")

    def get_phone_app(self):
        return self.config_file.read_string("Phone")

    def get_music_app(self):
        return self.config_file.read_string("Music")

    def get_maps_app(self):
        return self.config_file.read_string("Maps")

    def get_message_app(self):
        return self.config_file.read_string("Message")

    def get_exit_app(self):
        return self.config_file.read_string("Exit")