from Robo_FIT.GenericLibraries.GenericOpLibs.USBSwitch.ConfigurationReader import ConfigurationReader


class ConfigurationManager:
    """create the object of Configurator"""

    def __init__(self):
        self.config = ConfigurationReader()

    def get_device_name(self) -> str:
        return self.config.read_string("deviceName").upper()

    def get_device_id(self) -> str:
        return self.config.read_string("deviceId")

    def get_baudrate(self) -> int:
        return int(self.config.read_int("baudRate"))

    def get_devices(self) -> list:
        return self.config.read_list("devices")

    def get_port_number_for_name(self, required_device_name: str) -> int:
        required_port_num = None
        for device in self.config.read_list("devices"):
            if str(device["cntDeviceName"]) == str(required_device_name):
                required_port_num = int(device["portNumber"])
                break
        return required_port_num
