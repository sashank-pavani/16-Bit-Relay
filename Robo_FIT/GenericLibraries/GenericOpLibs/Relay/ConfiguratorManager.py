from Robo_FIT.GenericLibraries.GenericOpLibs.Relay.ConfigurationReader import ConfigurationReader



class ConfiguratorManager:

    def __init__(self):
        self.config = ConfigurationReader()

    def get_baud_rate(self):
        baud_rate = self.config.read_int("baudRate")
        if baud_rate == -1:
            raise ValueError("Invalid baudrate fro realy, Please check the configuration file of realy.")
        return baud_rate

    def get_device_id(self):
        device_id = self.config.read_string("deviceId")
        if device_id == "":
            raise ValueError(f"Device id for the realy is empty please check the configuration file")
        return device_id

    def get_vendor_name(self):
        device_name = self.config.read_string("deviceName")
        if device_name == "":
            raise ValueError("It seems device name is empty for the relay in configuration file of realy")
        return device_name.upper()

    def get_port_no(self, device: str):
        port_list = self.config.read_list("port")
        for data in port_list:
            if device.lower() == data["cntDeviceName"]:
                return data["portNumber"]
        raise ValueError("It seems port number and device name not provide in configuration file of Realy.")



