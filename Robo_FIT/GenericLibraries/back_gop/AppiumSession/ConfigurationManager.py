from Robo_FIT.GenericLibraries.GenericOpLibs.AppiumSession.ConfigurationReader import ConfiguratorReader


class ConfigurationManager:

    def __init__(self):
        self.config_reader = ConfiguratorReader()

    def get_hardware_port(self) -> str:
        return self.config_reader.read_string("hardwarePort")

    def get_bt_device_one_port(self) -> str:
        return self.config_reader.read_string("extPhoneOnePort")

    def get_bt_device_two_port(self) -> str:
        return self.config_reader.read_string("extPhoneTwoPort")

    def get_bt_device_three_port(self) -> str:
        return self.config_reader.read_string("extPhoneThreePort")

    def get_bt_device_four_port(self) -> str:
        return self.config_reader.read_string("extPhoneFourPort")
