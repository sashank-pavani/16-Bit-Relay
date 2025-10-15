import time
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_warning, \
    robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.HandleBarControl.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.SerialLogging.SerialLoggerHandler import SerialLoggerHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PRESS_TYPES


class HandleBarControlIDHandler:
    """
        This class is used for send serial QNX commands for Handle Bar Control.
    """

    def __init__(self):
        """
        This Constructor is used for initializing com_port of serial and ConfigurationManager class initialization
        for method to call which already defined.
        """
        try:
            self.config_manger = ConfigurationManager()
            self.serialobj = SerialLoggerHandler()
        except Exception:
            raise Exception("Access to Serial Failed : Please connect QNX Console to Respective Port")

    def create_frame(self, button_name: str, press_type: str = 'pressed') -> str:
        """
        This Function Create Frame for button pressed or released
        :param: button_name: (str): button name you want to press and release
        :param: press_type: (str): 'pressed':'01'(default_type) 'released':'00'
        :return: frame: (str): 0000<user_button_id><press_type>00
        """
        try:
            button_id = self.config_manger.get_button_id(button_name)
            if press_type == 'pressed':
                pressed_id = self.config_manger.get_pressed_id()
                return '0000' + button_id + pressed_id + '00'
            elif press_type == 'released':
                released_id = self.config_manger.get_released_id()
                return '0000' + button_id + released_id + '00'
            else:
                robot_print_error("Wrong Press Type mentioned, press_type should be from ['pressed','released']")
        except Exception as excp:
            robot_print_error(f"{excp}")

    def create_length_frame(self, frame: str) -> str:
        """
        This Function create length frame for given frame
        param frame: (str): frame value
        return: (str) : length frame
        """
        frame_length = len(frame) // 2
        return ' -l ' + str(frame_length)

    def create_cmd(self, button_name: str, press_type: str = 'pressed') -> str:
        """
        This Function create complete command for button pressed or released
        :param button_name: (str) button name you want to pressed or released
        :param press_type: (str) should be any one from ['pressed':01 (default), 'released':00]
        :return: (str) complete command to send
        """
        cmd = self.config_manger.get_cmd_id()
        message_group_value = self.config_manger.get_message_group_value()
        event_val = self.config_manger.get_event_value()
        message_count_val = self.config_manger.get_message_count_value()
        message_delay_val = self.config_manger.get_message_delay_value()
        wait_val = self.config_manger.get_wait_value()
        if press_type == 'pressed':
            pressed_frame = self.create_frame(button_name, press_type)
            pressed_length_frame = self.create_length_frame(pressed_frame)
            pressed_cmd = cmd + message_group_value + event_val + message_count_val + message_delay_val + wait_val + \
                          pressed_length_frame + ' -f' + pressed_frame + ' & \r\n'
            return pressed_cmd
        elif press_type == 'released':
            released_frame = self.create_frame(button_name, press_type="released")
            released_frame_length = self.create_length_frame(released_frame)
            released_cmd = cmd + message_group_value + event_val + message_count_val + message_delay_val + wait_val + \
                           released_frame_length + ' -f' + released_frame + '\r\n'
            return released_cmd

    def check_type_of_press_and_time(self, type_of_press: str = 'short', wait_time: int = None) -> int:
        """
        This Function Check wait_time -> default value is None
                                        if user not provide value of wait time it will search from json and
                                        if json also does not has wait time value then it throw an error.
        :param type_of_press: (str) Any one from ['short','long','stuck']
        :param wait_time: (str) wait time value default is None overwrite when user give value in parameter
        :return: (int) : wait time return
        """
        if type_of_press in PRESS_TYPES:
            if wait_time is not None:
                return wait_time
            elif wait_time is None:
                if type_of_press == 'short':
                    try:
                        ms = self.config_manger.get_short_press_wait_time()
                        robot_print_warning(f"Since Wait Time Not Given in Function Argument got it from json is :{ms}")
                        return int(ms)
                    except TypeError:
                        robot_print_error("Please Provide wait time at least one place either in function argument"
                                          " or in json config")
                elif type_of_press == 'long':
                    try:
                        ms = self.config_manger.get_long_press_wait_time()
                        robot_print_warning(f"Since Wait Time Not Given in Function Argument got it from json is :{ms}")
                        return int(ms)
                    except TypeError:
                        robot_print_error("Please Provide wait time at least one place either in function argument"
                                          " or in json config")
                else:
                    try:
                        ms = self.config_manger.get_stuck_press_wait_time()
                        robot_print_warning(f"Since Wait Time Not Given in Function Argument got it from json is :{ms}")
                        return int(ms)
                    except TypeError:
                        robot_print_error("Please Provide wait time at least one place either in function argument"
                                          " or in json config")
        else:
            robot_print_error("type_of_press should be any one from ['short','long','stuck']")

    def press_button(self, button_name: str, type_of_press: str = 'short', wait_time: int = None) -> None:
        """
        This Function creates below listed example commands:
        pressed:"vmf_sender -g 50 -e 0 -c 1 -d0 -w 0 -l 5 -f0000{}{}00 & \r\n".format(button_id, presssed_id)
        released:"vmf_sender -g 50 -e 0 -c 1 -d0 -w 0 -l 5 -f0000{}{}00\r\n".format(button_id,released_id)
        :param button_name: (str) :button name you want to press
        :param type_of_press: (str): default ='short' should be any one from list ['short','long','stuck']
        :param wait_time: (int) : time in 'milliseconds'

        :return: (None) : Nothing

        """
        pressed_cmd = self.create_cmd(button_name, 'pressed')
        released_cmd = self.create_cmd(button_name, 'released')
        ms_time = self.check_type_of_press_and_time(type_of_press, wait_time)
        self.serialobj.write_command_on_serial(device="qnx", cmd=pressed_cmd)
        time.sleep(ms_time / 1000)
        self.serialobj.write_command_on_serial(device="qnx", cmd=released_cmd)
