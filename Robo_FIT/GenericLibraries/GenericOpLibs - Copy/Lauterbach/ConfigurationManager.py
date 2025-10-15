from Robo_FIT.GenericLibraries.GenericOpLibs.Lauterbach.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class ConfiguratorManager:

    def __init__(self):
        self.config = ConfigurationReader.get_config_reader()

    def get_vip_scripts_path(self) -> str:
        try:
            return self.config.read_string('vip_scripts_path')
        except Exception as e:
            robot_print_error(f"Error to read the VIP Scripts path, EXCEPTION: {e}")

    def get_trace32_path(self) -> str:
        try:
            return self.config.read_string('trace32_path')
        except Exception as e:
            robot_print_error(f"Error to read the Trace32 installation Path, EXCEPTION: {e}")

    def get_application_name(self) -> str:
        try:
            return self.config.read_string('application_name')
        except Exception as e:
            robot_print_error(f"Error to read the Application name, EXCEPTION: {e}")

    def get_config_file_path(self) -> str:
        try:
            return self.config.read_string('config_file_path')
        except Exception as e:
            robot_print_error(f"Error to read the config file name, EXCEPTION: {e}")

    def get_config_file_name(self) -> str:
        try:
            return self.config.read_string('config_file_name')
        except Exception as e:
            robot_print_error(f"Error to read the config file name, EXCEPTION: {e}")

    def get_device_id(self) -> str:
        try:
            return self.config.read_string('device_id')
        except Exception as e:
            robot_print_error(f"Error to read the device id, EXCEPTION: {e}")

    def get_secure_boot_file_path(self) -> str:
        try:
            return self.config.read_string('Secure_boot_cmm_path')
        except Exception as e:
            robot_print_error(f"Error to read the scripts path, EXCEPTION: {e}")
