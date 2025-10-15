from Robo_FIT.GenericLibraries.GenericOpLibs.HandleBarControl.ConfigurationReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_warning, robot_print_error


class ConfigurationManager:

    def __init__(self):
        """
        Constructor of ConfigurationManager
        """
        self.config_file = ConfiguratorReader()

    def get_serial_port(self) -> str:
        """
        This Function is use to get Serial Port ID from handlebar_key_code_config.json
        :return (str): <user_serial_port_value>
        """
        return self.config_file.read_string("serialPort")

    def get_pressed_id(self) -> str:
        """
        This Function is use to get Pressed ID from handlebar_key_code_config.json
        :return (str): <user_pressed_value>
        """
        return self.config_file.read_string("pressed")

    def get_released_id(self) -> str:
        """
        This Function is use to get Released ID from handlebar_key_code_config.json
        :return (str): <user_released_value>
        """
        return self.config_file.read_string("released")

    def get_cmd_id(self) -> str:
        """
        This Function is use to get Command ID from handlebar_key_code_config.json
        :return: (str) : 'cmd' value defined in handlebar_key_code_config.json
        """
        command_info = self.config_file.read_list("cmdInfo")
        return command_info['cmd']

    def get_message_group_value(self) -> str:
        """
        This Function is use to get Message Group value from handlebar_key_code_config.json
         if value not present return default value of it
        :return: (str) : '-g <user_message_group_value>'
        """
        try:
            return ' -g ' + self.config_file.read_string("cmdInfo_arguments_messageGroup_value")
        except TypeError:
            try:
                default_value = ' -g ' + self.config_file.read_string("cmdInfo_arguments_messageGroup_default")
                robot_print_warning(f"Message Group Value not provided in JSON Config so,"
                                    f"default value {default_value} given")
                return default_value
            except TypeError:
                robot_print_error(" Message Group Value and Default Value both missing in json config!!")

    def get_event_value(self) -> str:
        """
        This Function is use to get event value from handlebar_key_code_config.json
        if value not present return default value of it
        :return: (str) : '-e <user_event_value>'
        """
        try:
            return ' -e ' + self.config_file.read_string("cmdInfo_arguments_event_value")
        except TypeError:
            try:
                default_value = ' -e ' + self.config_file.read_string("cmdInfo_arguments_event_default")
                robot_print_warning(f"Event Value not provided in JSON Config so,"
                                    f"default value {default_value} given")
                return default_value
            except TypeError:
                robot_print_error(" Event Value and Default Value both missing in json config!!")

    def get_message_count_value(self) -> str:
        """
        This Function is use to get message count value from handlebar_key_code_config.json
        if value not present return default value of it
        :return: (str) : '-c <user_message_count_value>'
        """
        try:
            return ' -c ' + self.config_file.read_string("cmdInfo_arguments_messageCount_value")
        except TypeError:
            try:
                default_value = ' -c ' + self.config_file.read_string("cmdInfo_arguments_messageCount_default")
                robot_print_warning(f"Message Count Value not provided in JSON Config so,"
                                    f"default value {default_value} given")
                return default_value
            except TypeError:
                robot_print_error(" Message Count Value and Default Value both missing in json config!!")

    def get_message_delay_value(self) -> str:
        """
        This Function is use to get message delay value from handlebar_key_code_config.json
        if value not present return default value of it
        :return: (str) : '-d <user_message_delay_value>'
        """
        try:
            return ' -d ' + self.config_file.read_string("cmdInfo_arguments_messageDelay_value")
        except TypeError:
            try:
                default_value = ' -d ' + self.config_file.read_string("cmdInfo_arguments_messageDelay_default")
                robot_print_warning(f"Message delay Value not provided in JSON Config so,"
                                    f"default value {default_value} given")
                return default_value
            except TypeError:
                robot_print_error(" Message delay Value and Default Value both missing in json config!!")

    def get_wait_value(self) -> str:
        """
        This Function is use to get wait value from handlebar_key_code_config.json
        if value not present return default value of it
        :return: (str) : '-w <user_wait_value>'
        """
        try:
            return ' -w ' + self.config_file.read_string("cmdInfo_arguments_wait_value")
        except TypeError:
            try:
                default_value = ' -w ' + self.config_file.read_string("cmdInfo_arguments_wait_default")
                robot_print_warning(f"Wait Value not provided in JSON Config so,"
                                    f"default value {default_value} given")
                return default_value
            except TypeError:
                robot_print_error(" Wait Value and Default Value both missing in json config!!")

    def get_short_press_value(self) -> str:
        """
        This Function is use to get short press value from handlebar_key_code_config.json
        :return: (str) : '<user_short_press_value>'
        """
        return self.config_file.read_string("pressInfo_short_value")

    def get_short_press_wait_time(self) -> str:
        """
        This Function is use to get short press wait time value from handlebar_key_code_config.json
        :return: (str) : '<user_short_press_wait_time_value>'
        """
        return self.config_file.read_string("pressInfo_short_waitTime")

    def get_long_press_value(self) -> str:
        """
        This Function is use to get long press value from handlebar_key_code_config.json
        :return: (str) : '<user_long_press_value>'
        """
        return self.config_file.read_string("pressInfo_long_value")

    def get_long_press_wait_time(self) -> str:
        """
        This Function is use to get long press wait time value from handlebar_key_code_config.json
        :return: (str) : '<user_long_press_wait_time_value>'
        """
        return self.config_file.read_string("pressInfo_long_waitTime")

    def get_stuck_press_value(self) -> str:
        """
        This Function is use to get stuck press value from handlebar_key_code_config.json
        :return: (str) : '<user_stuck_press_value>'
        """
        return self.config_file.read_string("pressInfo_stuck_value")

    def get_stuck_press_wait_time(self) -> str:
        """
        This Function is use to get stuck press wait time value from handlebar_key_code_config.json
        :return: (str) : '<user_stuck_press_wait_time_value>'
        """
        return self.config_file.read_string("pressInfo_stuck_waitTime")

    def get_button_id(self, button: str) -> str:
        """
        This Function is used to get button id
        param: button: (str): button name
        return: button ID from handlebar_key_code_config.json
        """
        try:
            return self.config_file.read_string("buttonsId_" + button.lower())
        except KeyError:
            raise KeyError(f"please check '{button}' name should be same as given in handlebar_key_code_config.json")
