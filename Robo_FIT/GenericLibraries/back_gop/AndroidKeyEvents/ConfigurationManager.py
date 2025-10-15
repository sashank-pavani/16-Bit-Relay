from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidKeyEvents.ConfigurationReader import ConfiguratorReader


class ConfigurationManager:

    def __init__(self):
        """
        Constructor of ConfiguratioManager
        :param config_path: global file configuraton path and parameter passed by UserADBLogger class
        """
        self.config_file = ConfiguratorReader()

    def android_device_id(self) -> str:
        return self.config_file.read_string("adbDeviceId")

    def get_key_code(self, key: str):
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes[key].strip()

    def volume_up_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["volumeUp"].strip()

    def volume_down_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["volumeDown"].strip()

    def volume_mute_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["volumeMute"].strip()

    def media_next_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["mediaNext"].strip()

    def media_previous_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["mediaPrevious"].strip()

    def media_pause_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["mediaPause"].strip()

    def media_play_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["mediaPlay"].strip()

    def up_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["up"].strip()

    def down_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["down"].strip()

    def left_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["left"].strip()

    def right_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["right"].strip()

    def ok_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["ok"].strip()

    def setting_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["setting"].strip()

    def call_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["call"].strip()

    def media_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["media"].strip()

    def phone_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["phone"].strip()

    def favorite_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["favorite"].strip()

    def source_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["source"].strip()

    def back_key_code(self) -> str:
        key_codes = self.config_file.read_list("swcKeyCodes")
        return key_codes["back"].strip()
