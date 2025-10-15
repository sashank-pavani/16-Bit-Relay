from Robo_FIT.GenericLibraries.GenericOpLibs.TelematicControlUnit.TCUService.ConfiguratorReader import ConfiguratorReader


class ConfigurationManager:

    def __init__(self):
        self.config_reader = ConfiguratorReader()

    def get_broker_address(self) -> str:
        return self.config_reader.read_string("brokerAddress")

    def get_port_number(self) -> int:
        return self.config_reader.read_int("port")

    def get_user_id(self) -> str:
        return self.config_reader.read_string("userId")

    def get_user_password(self) -> str:
        return self.config_reader.read_string("userPassword")

    def get_tcu_vin_number(self) -> str:
        return self.config_reader.read_string("vinNumber")

    def get_tcu_din_number(self) -> str:
        return self.config_reader.read_string("dinNumber")

    def get_input_excel_path(self) -> str:
        return self.config_reader.read_string("inputExcel")

