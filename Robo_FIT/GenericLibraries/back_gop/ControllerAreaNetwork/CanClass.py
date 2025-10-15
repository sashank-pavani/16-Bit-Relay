import os
from datetime import time
from time import sleep

import can
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import VECTOR_CAN_BUS_TYPE, VECTOR_APP_NAME_LIST
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PCAN_BUS_TYPE, PCAN_CHANNEL_LIST
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ICan import ICan
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.VectorCANClass import VectorCANClass
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.PCANClass import PCANClass
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from typing import Union


class CanClass(ICan):
    """
    This function call VectorCAN class Methods
    """

    def __init__(self, channel_name):
        self.config_manager = ConfigurationManager()
        self.can_instance: None
        # self.can_instance: VectorCANClass
        # self.__initialize_can(channel_name)

    # def __initialize_can(self, channel_name):
        app_name = self.config_manager.get_app_name()
        bus_type = self.config_manager.get_bus_type()
        if bus_type == VECTOR_CAN_BUS_TYPE:
            if app_name in VECTOR_APP_NAME_LIST:
                robot_print_debug(f"Initializing CAN for device: {VECTOR_CAN_BUS_TYPE}")
                self.can_instance = VectorCANClass(channel_name=channel_name)
            else:
                robot_print_error(text=f"Invalid App Name {app_name}. Please Provide app_name from"
                                       f" {VECTOR_APP_NAME_LIST} in can_config_file.json", underline=True)
        elif bus_type == PCAN_BUS_TYPE:
            self.can_instance = PCANClass(channel_name=channel_name)

        else:
            robot_print_error(text=f"Invalid Bus type {bus_type}. Please provide correct busType"
                                   " in can_config_file.json", underline=True)
            raise AttributeError("Error to initialize the CAN, "
                                 "Wrong attribute pass in configuration file.")

    def get_rx_message(self, database_num: int = 1):
        """
        :return: Return True if any RX message found
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        value = self.can_instance.get_rx_message(database_num)
        if value:
            return True
        else:
            return False

    def stop_can_trace(self, data_num: int = 1):
        """
        This Function Stop Vector/PCAN Trace
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        self.can_instance.stop_can_trace(data_num)

    def start_can_trace(self, interval, database_num: int = 1):

        """
        This Function starts the vector/PCAN trace with user given interval
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        self.can_instance.start_can_trace(database_num=int(database_num), interval=interval)

    def start_time_rotate_logs(self, when: str, interval: int, backup_count: int, database_num: int = 1):
        """
        This Function starts can trace with time rotating log files for Vector/PCAN Trace
        - database_num: channel /database number in integer
        - interval: log the CAN data based on this interval in integer
        - when: string value, M for minutes , D for days and S for second in string
        - backup_count: number files to be retained after deleting the last file in integer
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        self.can_instance.start_time_rotate_logs(database_num=int(database_num), when=when, interval=interval,
                                                 backup_count=backup_count)

    def send_can_signal_periodically(self, can_des: str, database_num: int = 1, signal_type: str = "TX",
                                     periodicity: int = 100) -> can.CyclicSendTaskABC:
        """
        This Function send can signal Periodically as per can_des and signal type given by user
        :param periodicity: default periodicity is set to 100 sec
        :param can_des: any value From CAN_DES Column of CAN_Input_Excel.xlsx
        :param database_num: database number /channel number set default to channel 1
        :database_num:
        :param signal_type: signal type options are CAN_Input_Excel.xlsx sheet names
        :return: task id
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        return self.can_instance.send_can_signal_periodically(can_des=can_des, database_num=int(database_num),
                                                              signal_type=signal_type)

    def send_can_signal(self, can_des: str, database_num: int = 1):
        """
        This Function send can signal
        :param can_des:  any value From CAN_DES Column of CAN_Input_Excel.xlsx
        :param database_num: CAN description mention in InputFile
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        self.can_instance.send_can_signal(can_des=can_des, database_num=int(database_num))

    def stop_can_periodically_signal(self, task: can.CyclicSendTaskABC):
        """
        This Function use to stop can periodic signal using task id
        :param task: task id got from send_can_signal_periodically
        """
        if self.can_instance is None:
            raise TypeError("CAN  is not initialize, the object is none. Please check the logs")
        self.can_instance.stop_can_periodically_signal(task=task)

    def shut_down_can_bus(self, database_num: int):
        """
        To shout down can bus
        """
        if self.can_instance is None:
            raise TypeError("CAN  is not initialize, the object is none. Please check the logs")
        return self.can_instance.shut_down_can_bus(int(database_num))

    def receive_can_message_data(self, can_des: str, database_num: int = 1, timeout: int = 10, is_list: bool = True,
                                 is_dict: bool = False) \
            -> Union[list, dict]:
        """
        This Function Returns Data of Message based on can des provided in CAN_input_Excel.xlsx
        :param can_des: can_des: CAN description in the Excel file
        :param database_num: database number /channel number
        :param timeout: optional, Default value if 10 second. If user required more time than change
        the value in seconds
        :param is_list: data format user want as output in list then make it True else False
        :param is_dict: data format user want as output in list then make it True else False
        :return:list or dict time format output as per is_list or is_dict option selected by user
        """
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        return self.can_instance.receive_can_message_data(can_des=can_des, database_num=database_num, timeout=timeout,
                                                          is_list=is_list,
                                                          is_dict=is_dict)

    def get_specific_message(self, database_num, specific_message_id_hex):
        if self.can_instance is None:
            raise TypeError("CAN is not initialize, the object is none. Please check the logs")
        value = self.can_instance.get_specific_message(database_num, specific_message_id_hex)
        if value:
            return True
        else:
            return False