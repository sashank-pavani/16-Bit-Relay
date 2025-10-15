import os
import concurrent.futures
import shutil
import re
import sys
import threading
from datetime import datetime
from threading import Event
from time import sleep
from typing import Tuple, Any, Union

import cantools
import can
from can import CanError

from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.CANInputFileParsing.CanInputFileParsing import \
    CanInputFileParsing
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.CanBus import CanBus
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.GetCanTrace import GetCanTrace
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ICan import ICan
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info


class VectorCANClass(ICan):
    """
    This Class is use for CAN Signal Send using Vector Family Tools like CANoe or CANalyzer etc.
    """
    # CAN Tupe
    __CAN_MESSAGE_NAME = "messageName"
    __CAN_SIGNAL_TYPE_TX = "TX"
    __CAN_SIGNAL_TYPE_MASTER = "MASTER"
    # CAN Data
    __CAN_TASK_ID = "taskID"
    __CAN_SIGNAL_OCCURRENCE = "occurrence"
    __CAN_IS_CRC = "isCrc"
    __CAN_SIGNAL_ONCE = "once"
    __CAN_SIGNAL_PERIODIC = "periodic"
    __CAN_SIGNAL_STATUS = "status"
    __CAN_SIGNAL_RUNNING = "running"
    __CAN_SIGNAL_STOP = "stop"
    __CAN_SIGNAL_TYPE = "type"
    __CAN_SIGNAL_FUTURE_OBJECT = None
    __feature_stop_dict = {}

    # Variables initialize
    _stop_can_signal = 0
    __master_can_signal_task_list = []
    __can_signal_data_dict = {}
    __is_master_signal_send = False
    __is_crc_stop = False
    __rollback_ids = []
    __signal_db_dict = {}
    # create event for Thread stop
    __EVENT = Event()

    __crc_store = {}

    def __init__(self, channel_name):
        try:
            self.config_manager = ConfigurationManager()
            self.read_input_file_data = CanInputFileParsing(channel_name)
            self.can_bus1 = self.__create_vector_can_bus(1, channel_name=channel_name)
            robot_print_info(f"Inside Get Can trace , CAN Object is : {id(self.can_bus1)}")
            if channel_name == 'dual':
                self.can_bus2 = self.__create_vector_can_bus(2, channel_name=channel_name)
                robot_print_info(f"Inside Get Can trace , CAN Object is : {id(self.can_bus2)}")
                self.file_name_ch2 = self.__can_trace_file_name('dual')
                robot_print_info(f"can trace file name for second channel:{self.file_name_ch2}")
                self.get_can_trace_ch2 = GetCanTrace(self.can_bus2, file_name=self.file_name_ch2)
            # create thread object for CRC
            self.crc_thread = concurrent.futures.ThreadPoolExecutor(max_workers=60)
            # getting rollback arbitration ids
            self.__get_roll_back_ids()
            # start CAN Trace
            self.file_name_ch1 = self.__can_trace_file_name('single')
            robot_print_info(f"can trace file name for First channel:{self.file_name_ch1}")
            self.get_can_trace_ch1 = GetCanTrace(self.can_bus1, file_name=self.file_name_ch1)
            self.is_start_can_trace = self.config_manager.get_can_trace_enable()
            # to get the user input for get can trace interval
            self.is_interval_can_trace_given = self.config_manager.get_interval_trace_enable()
            self.is_send_can_master_signal = self.config_manager.get_master_signal_status()
            # robot_print_debug(f"isSendCanMasterSignal Value: {self.is_send_can_master_signal}")
            self.can_message_handler = CanFrameHandler()
            if self.is_send_can_master_signal and not VectorCANClass.__is_master_signal_send:
                # Start sending CAN master signals
                self.__send_master_signal(1)
                self.__send_master_signal(2)
            elif not VectorCANClass.__is_master_signal_send:
                robot_print_warning("Either you set CAN 'isSendCanMasterSignal' value 'False' in configuration file, "
                                    "(\"isSendCanMasterSignal\": \"false\") or you provide wrong value in config file"
                                    "\nSo We are not sending the CAN Master signals, If you want to send CAN master "
                                    "signals\nyou need to set (\"isSendCanMasterSignal\": \"true\")")
            if self.is_start_can_trace:
                self.get_can_trace_ch1.get_all_trace()
                robot_print_info(f"starting the trace for 1st bus")
                sleep(2)
                if channel_name == 'dual':
                    self.get_can_trace_ch2.get_all_trace()
                    robot_print_info(f"starting the trace for 2nd bus")
                    sleep(2)
            else:
                robot_print_warning("Either you set CAN trace disable in configuration file, "
                                    "(\"canTraceEnable\": \"false\") or you provide wrong value in config file")
        except CanError as can_error:
            self.can_bus1 = None
            self.can_bus2 = None
            robot_print_error(f"There is error to create CAN Bus, Exception:{can_error}")
            sys.exit()

    def __get_roll_back_ids(self):
        if len(VectorCANClass.__rollback_ids) == 0:
            VectorCANClass.__rollback_ids = self.config_manager.get_roll_back_ids()

    def __can_trace_file_name(self, channel_name) -> str:
        """
        This method check for the file name
        If filename is correct which is provided by the user in config file
        then it returns that filename otherwise it uses default file name
        i.e. can_trace.asc
        :return: Filename if correct name provided by user otherwise default
                `can_trace.asc`
        """
        file_name = self.config_manager.get_can_trace_file_name_ch(channel_name)
        file_datetime = datetime.now().strftime("_%d_%b_%Y_%H_%M_%S")
        file_name = file_name.split(".")[0] + file_datetime + "." + file_name.split(".")[1]
        file_name = self.config_manager.get_can_trace_file_path(file_name)
        if file_name.endswith(".asc"):
            return file_name
        elif file_name.endswith(".blf"):
            return file_name
        elif file_name.endswith(".csv"):
            return file_name
        elif file_name.endswith(".db"):
            return file_name
        elif file_name.endswith(".log"):
            return file_name
        elif file_name.endswith(".txt"):
            return file_name
        else:
            robot_print_warning(f"Unknown file name ({file_name}) for the CAN"
                                f" trace, So we are using default file name i.e. can_trace.asc")
            f_name = "can_trace" + file_datetime + ".asc"
            default_file_name = self.config_manager.get_can_trace_file_path(f_name)
            return default_file_name

    def __create_vector_can_bus(self, database_num, channel_name) -> object:
        """
        This method is used to create the CAN bus objects for two channels.
        :return: Dictionary containing CAN bus objects for each channel.
        """

        bus_instances = {}
        bus_type = self.config_manager.get_bus_type()
        app_name = self.config_manager.get_app_name()

        bit_rate_ch1 = self.config_manager.get_bit_rate("single")
        channel_ch1 = self.config_manager.get_channel("single")
        if channel_name == "dual":
            channel_ch2 = self.config_manager.get_channel("dual")
            bit_rate_ch2 = self.config_manager.get_bit_rate("dual")
            bus_instances[1] = CanBus.get_can_bus_instance(bus_type=bus_type, app_name=app_name, bit_rate=bit_rate_ch1,
                                                           channel=int(channel_ch1))
            bus_instances[2] = CanBus.get_can_bus_instance(bus_type=bus_type, app_name=app_name, bit_rate=bit_rate_ch2,
                                                           channel=int(channel_ch2))
            robot_print_info(f"successfully created bus instances:{bus_instances}")

            if database_num == 1:
                return bus_instances[1]
            elif database_num == 2:
                return bus_instances[2]
        if channel_name == "single":
            bus_instances[1] = CanBus.get_can_bus_instance(bus_type=bus_type, app_name=app_name, bit_rate=bit_rate_ch1,
                                                           channel=int(channel_ch1))
            return bus_instances[1]

    def __is_msg_contain_crc(self, message: cantools.db.Message, database_num, user_data: bytearray) -> bool:
        """
        This function will check that message contains the CRC value or not.
        :param user_data: user data in json format
        :param message: Message obj
        :return: True if CRC value in message otherwise False
        """
        message_name = message.name
        try:
            json_data = self.read_input_file_data.get_decoded_data(message_name, database_num, user_data)
            robot_print_debug(json_data)
            for key in json_data.keys():
                if "CRC" in key.upper():
                    robot_print_debug(f"Message: {message_name} contains CRC as {key}", print_in_report=True)
                    return True
            robot_print_debug(f"Message: {message_name} not contain CRC value", print_in_report=True)
            return False
        except Exception as exp:
            robot_print_error(f"Error to check the CRC value of the {message_name}, EXCEPTION: {exp}")
            return False

    def __create_can_message(self, can_des: str, database_num, signal_type: str = "TX") -> [str, can.Message, bytearray,
                                                                                            cantools.db.Message]:
        """
        This method is used to create the CAN message. It read the message form the InputFile.
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        :return: "CAN message" if successfully created otherwise "None"
        """
        try:
            message_name = self.read_input_file_data.get_can_message_name(can_des=can_des, database_num=database_num,
                                                                          signal_type=signal_type)
            robot_print_info(f"message_name:{message_name}")
            if message_name is not None:
                # dbc_Message
                robot_print_info(f"database_num:{database_num}")
                can_message = self.read_input_file_data.get_msg_object_by_msg_name(message_name=message_name,
                                                                                   database_num=database_num)
                # XL data user given
                user_data = self.read_input_file_data.get_can_data(can_des=can_des, database_num=database_num,
                                                                   signal_type=signal_type)
                robot_print_info(f"DATA_TO_SEND : {user_data}")
                extended_id = can_message.is_extended_frame
                #message_frame = can.Message(arbitration_id=can_message.frame_id, data=user_data,
                                            #is_extended_id=extended_id, is_rx=False)
                message_frame = can.Message(arbitration_id=can_message.frame_id, data=user_data,
                                            is_extended_id=extended_id, is_fd=True, bitrate_switch=True)
                return message_name, message_frame, user_data, can_message
            else:
                raise ValueError(f"Message Object got None for can_des={can_des} signal_type={signal_type}")
        except can.CanError as can_error:
            robot_print_error(f"There is an exception to create CAN message,\nException: {can_error}")
            return None

    def __send_can_crc_signal(self, db_message: cantools.db.Message, user_data: bytearray, periodic_time: int
                              , database_num) -> Tuple[can.CyclicSendTaskABC, Any]:
        """
        This method send the CAN signal which contain CRC value
        :param db_message: message obj
        :param user_data: user data
        :return: task id , future_obj
        """
        try:
            data = bytearray(user_data)
            future_obj = None
            task = None
            # robot_print_info(f"VectorCANClass.__feature_stop_dict{VectorCANClass.__feature_stop_dict}")
            if db_message.name not in VectorCANClass.__feature_stop_dict:
                VectorCANClass.__feature_stop_dict[db_message.name] = 1
            else:
                VectorCANClass.__feature_stop_dict[db_message.name] += 1
            # Create CAN message frame
            can_message_frame = can.Message(arbitration_id=db_message.frame_id, data=data,
                                            is_extended_id=db_message.is_extended_frame, is_rx=False)
            if VectorCANClass.__can_signal_data_dict.get(db_message.name) is not None and \
                    VectorCANClass.__can_signal_data_dict[db_message.name][
                        VectorCANClass.__CAN_SIGNAL_STATUS] == VectorCANClass.__CAN_SIGNAL_RUNNING:
                robot_print_info(f"CRE thread is already running for {db_message.name}")
                self.can_message_handler.set_can_message_frame(can_message_frame.data, db_message.name)
                task = VectorCANClass.__can_signal_data_dict[db_message.name][VectorCANClass.__CAN_TASK_ID]
                future_obj = VectorCANClass.__can_signal_data_dict[db_message.name][
                    VectorCANClass.__CAN_SIGNAL_FUTURE_OBJECT]
            else:
                # Start sending the task and store task ID to stop the CAN signal in future
                task = None
                if database_num == 1:
                    task = self.can_bus1.send(can_message_frame, period=periodic_time)
                    robot_print_debug(f"CAN message {db_message.name} Task id :{task}")
                elif database_num == 2:
                    task = self.can_bus2.send(can_message_frame, period=periodic_time)
                self.can_message_handler.set_can_message_frame(can_message_frame.data, db_message.name)
                self.__can_record_data(db_message.name, task, signal_type="TX", is_crc=True)
                # VectorCANClass.__can_signal_data_dict[db_message.name][VectorCANClass.__CAN_TASK_ID] = task
                future_obj = self.crc_thread.submit(self.__start_crc_signal_thread, db_message, periodic_time,
                                                    database_num)
                robot_print_debug(f"Future Object future_obj Status:{future_obj.running()}")
                while not future_obj.running() and future_obj.exception() is None:
                    robot_print_debug(f"Waiting for thread to start", print_in_report=True)
                    sleep(10)
                robot_print_info(f"CRC Thread start now for {db_message.name}")
                # storing the future object into Store
                VectorCANClass.__can_signal_data_dict[db_message.name][
                    VectorCANClass.__CAN_SIGNAL_FUTURE_OBJECT] = future_obj
            return task, future_obj
        except Exception as exp:
            robot_print_error(f"Error to send the CAN signal which contain CRC value, EXCEPTION: {exp}")

    def __send_can_crc_signal_modify(self, db_message: cantools.db.Message, user_data: bytearray,
                                     periodic_time, data_num) -> can.CyclicSendTaskABC:
        message_name = db_message.name
        try:
            if VectorCANClass.__can_signal_data_dict.get(message_name) is not None and \
                    VectorCANClass.__can_signal_data_dict[message_name][
                        VectorCANClass.__CAN_SIGNAL_STATUS] == VectorCANClass.__CAN_SIGNAL_RUNNING:
                # Signals already sending for given message, just need to update the frame
                robot_print_info(f"for message: {message_name}, CRC is already running")
                self.can_message_handler.set_can_message_frame(user_data, db_message.frame_id)
            else:
                # send a new periodic signal for give message
                robot_print_info(f"for message: {message_name}, creating CRC")
                rc_signal_len = self.__get_roll_count_msg_length(db_msg=db_message)
                mask = int("11111111"[0:8 - rc_signal_len].ljust(8, "0")[:8], 2)
                can_rc_handler = CalculateRcValue(frame=user_data, rc_len=rc_signal_len,
                                                  rc_max_value=2 ** rc_signal_len, mask=mask)
                # user_data[6] = can_rc_handler.get_rc_next_value()
                self.can_message_handler.set_can_message_frame(user_data, db_message.frame_id)
                VectorCANClass.__crc_store[db_message.frame_id] = can_rc_handler
                can_message = can.Message(arbitration_id=db_message.frame_id, data=user_data,
                                          is_extended_id=db_message.is_extended_frame, is_rx=False)
                if data_num == 1:
                    task = self.can_bus1.send_periodic(can_message, periodic_time, store_task=True,
                                                       modifier_callback=self.on_message_update)
                if data_num == 2:
                    task = self.can_bus2.send_periodic(can_message, periodic_time, store_task=True,
                                                       modifier_callback=self.on_message_update)
                self.__can_record_data(db_message.name, task, signal_type="TX", is_crc=True)
                # VectorCANClass.__can_signal_data_dict[message_name][
                #     VectorCANClass.__CAN_SIGNAL_STATUS] = VectorCANClass.__CAN_SIGNAL_RUNNING
                # VectorCANClass.__can_signal_data_dict[message_name][VectorCANClass.__CAN_TASK_ID] = task
                return task
        except can.CanError as exp:
            robot_print_error(f"Error to send the can CRC signal for message: {message_name}, EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(
                f"Unknown error while sending CRC signal for message: {message_name}, EXCEPTION: {exp}")

    def __get_roll_count_msg_length(self, db_msg: cantools.db.Message):
        try:
            for signal in db_msg.signals:
                match = re.search("(?i)(rollcount)", signal.name)
                if match:
                    # robot_print_info(f"Found the roll count message with name '{signal.name}' "
                    #                  f"and its length is '{signal.length}'")
                    return int(signal.length)
            # robot_print_error(f"Given message: {db_msg} no contain roll count")
        except Exception as exp:
            robot_print_error(f"Error to check if roll count is in db message: {db_msg}, EXCEPTION: {exp}")

    def __start_crc_signal_thread(self, db_msg: cantools.db.Message, timeout, database_num):
        try:
            while VectorCANClass.__can_signal_data_dict[db_msg.name][VectorCANClass.__CAN_SIGNAL_STATUS] == \
                    VectorCANClass.__CAN_SIGNAL_RUNNING:
                if db_msg.frame_id in VectorCANClass.__rollback_ids:
                    data = self.can_message_handler.get_can_message_frame(db_msg.name)
                    data[6] = CanBus.calculate_rc(data)
                    data[7] = CanBus.calculate_checksum(data)
                    can_message_frame = can.Message(arbitration_id=db_msg.frame_id, data=data,
                                                    is_extended_id=db_msg.is_extended_frame, is_rx=False)
                    if database_num == 1:
                        task = self.can_bus1.send(can_message_frame, period=timeout)
                    elif database_num == 2:
                        task = self.can_bus2.send(can_message_frame, period=timeout)
                    sleep(timeout)

        except Exception as exp:
            robot_print_error(f"Error to run the CRC thread, EXCEPTION {exp}")

    def on_message_update(self, message: can.Message):
        try:
            # robot_print_debug(f"for message: {message.arbitration_id}, on message update, data: {[int(i) for i in message.data]}")
            data = self.can_message_handler.get_can_message_frame(message_name=message.arbitration_id)
            if data is not None:
                message.data = data
            if VectorCANClass.__crc_store.get(message.arbitration_id) is not None and VectorCANClass.__crc_store[
                message.arbitration_id] is not None:
                message.data[6] = VectorCANClass.__crc_store[message.arbitration_id].get_rc_next_value(message.data,
                                                                                                       message.arbitration_id)
                message.data[7] = CanBus.calculate_checksum(message.data)
        except Exception as exp:
            robot_print_error(f"Error to modify the frame, EXCEPTION: {exp}")

    def __send_crc_signal_in_thread(self, task: can.ModifiableCyclicTaskABC, db_msg: cantools.db.Message,
                                    data: bytearray, database_num) -> None:
        """
        This Function send can crc signal in thread with updated message step count and CRC check sum calculated value
        :param task: task id
        :param db_msg: message obj
        :param data: user data
        """
        try:
            can_message = db_msg.name
            robot_print_info(f"In CRC thread dict is: {VectorCANClass.__can_signal_data_dict}")
            max_step_count = self.read_input_file_data.get_max_step_count(can_message, database_num=database_num)
            robot_print_info(f"Message MAX Step Count:{max_step_count}")
            current_count = data[6]
            while VectorCANClass.__can_signal_data_dict[can_message][VectorCANClass.__CAN_IS_CRC]:
                if current_count == max_step_count + 1:  # todo:changes made
                    # If current count increase to max_step_count make it 0 again
                    current_count = 0
                else:
                    # increase current count with user provide step count
                    current_count += 1
                # replace second last and last value with message amd CRC respectively.
                data[6] = current_count
                crc_table = CanBus.calculate_table_crc()
                if crc_table is not None:
                    crc_check_sum = CanBus.calculate_checksum(data)
                    if crc_check_sum is not None:
                        data[7] = crc_check_sum
                    else:
                        raise Exception("CRC Check sum Calculation Failed!!!")
                else:
                    raise Exception("CRC Calculation Failed!!!")
                # create the data into bytearray
                data = bytearray(data)
                # create the CAN message frame again
                can_message_frame = can.Message(arbitration_id=db_msg.frame_id, data=data,
                                                is_extended_id=False, is_rx=False)
                # send the modify data
                # robot_print_debug(f"Frame after CRC calculation : {can_message_frame}", print_in_report=True)
                task.modify_data(can_message_frame)
        except Exception as exp:
            robot_print_error(f"Error to create the thread for CRC signal, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}", print_in_report=True)

    def __print_can_message(self, msg: can.Message) -> None:
        """
        This method is used to print the given CAN message
        :param msg: message
        :return:None
        """
        try:
            printer = can.Printer()
            printer.on_message_received(msg)
        except can.CanError as can_error:
            robot_print_error(f"There is an exception to print the CAN messages,\nException: {can_error}")

    def __can_record_data(self, can_message_name: str,
                          task: Union[None, can.ModifiableCyclicTaskABC, can.CyclicSendTaskABC],
                          signal_type: str, is_crc: bool):
        try:
            if can_message_name not in VectorCANClass.__can_signal_data_dict.keys():
                VectorCANClass.__can_signal_data_dict[can_message_name] = {}
            VectorCANClass.__can_signal_data_dict[can_message_name][
                VectorCANClass.__CAN_TASK_ID] = task
            VectorCANClass.__can_signal_data_dict[can_message_name][
                VectorCANClass.__CAN_SIGNAL_OCCURRENCE] = VectorCANClass.__CAN_SIGNAL_PERIODIC
            VectorCANClass.__can_signal_data_dict[can_message_name][
                VectorCANClass.__CAN_SIGNAL_STATUS] = VectorCANClass.__CAN_SIGNAL_RUNNING
            VectorCANClass.__can_signal_data_dict[can_message_name][
                VectorCANClass.__CAN_SIGNAL_TYPE] = signal_type
            VectorCANClass.__can_signal_data_dict[can_message_name][
                VectorCANClass.__CAN_IS_CRC] = is_crc
            robot_print_debug(f"CAN Record: {VectorCANClass.__can_signal_data_dict}", True)
        except Exception as exp:
            robot_print_error(f"Error to add the CAN message into CAN record, EXCEPTION: {exp}")

    def __send_master_signal(self, database_num) -> None:
        """
        This method is used to send the CAN master signals.
        This method fetch the CAN des from the CAN input Excel sheet and send the CAN signal one by one.
        User need to mention all master CAN signal into CAN input Excel file. These methods fetch all the
        value into list and then start sending the signals
        :return: None
        """
        try:
            if not VectorCANClass.__is_master_signal_send:
                # get the CAN des in list
                can_des_list = self.read_input_file_data.get_master_can_signal_des()
                robot_print_debug(f"CAN message list: {can_des_list}", True)
                for can_des in can_des_list:
                    # send the CAN master signal one by one
                    task = self.send_can_signal_periodically(can_des=can_des,
                                                             signal_type=VectorCANClass.__CAN_SIGNAL_TYPE_MASTER,
                                                             database_num=database_num)
                    robot_print_info(f"CAN signal {can_des} send with task id: {task}")
                    # append the task into global variable. So that can stop later
                    VectorCANClass.__master_can_signal_task_list.append(task)
                    if len(can_des_list) == len(VectorCANClass.__master_can_signal_task_list):
                        VectorCANClass.__is_master_signal_send = True
                robot_print_info(
                    f"{len(VectorCANClass.__master_can_signal_task_list)} number's of CAN Master signal send"
                    f" successfully")
        except can.CanError as can_err:
            robot_print_error(f"Error in master signal, EXCEPTION: {can_err}")
        except Exception as exp:
            robot_print_error(f"Error to send the CAN master signal, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)

    def send_can_signal(self, can_des: str, database_num: int = 1) -> None:
        """
        This method is used to send the CAN signal.
        :param can_des: CAN description mention in InputFile
        :param database_num: CAN description mention in InputFile
        :return: None
        """
        try:
            message_name, message, user_data, can_message = self.__create_can_message(can_des=can_des,
                                                                                      database_num=int(database_num)
                                                                                      )
            robot_print_debug(f"message:{user_data}", True)
            if message is not None:
                if can_message.frame_id in VectorCANClass.__rollback_ids:
                    user_data[6] = CanBus.calculate_rc(user_data)
                is_crc = self.__is_msg_contain_crc(can_message, database_num, user_data)
                if is_crc:
                    user_data[7] = CanBus.calculate_rc(user_data)
            if database_num == 1:
                if message is not None:
                    self.can_bus1.send(message)
                    self.__print_can_message(msg=message)
                else:
                    robot_print_error("CAN Message is None...!!!")
            if database_num == 2:
                if message is not None:
                    self.can_bus2.send(message)
                    self.__print_can_message(msg=message)
                else:
                    robot_print_error("CAN Message is None...!!!")
        except can.CanError as can_error:
            robot_print_debug("There is an exception to send the CAN signal,\nException:{can_error}", True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)

    def __check_can_signal_status(self, message_name: str) -> (bool, can.ModifiableCyclicTaskABC):
        """
        This Function check CAN signal status if already running or not !!!
        :param message_name: message name
        :return: True:signal still running else false , Task_id
        """
        try:
            robot_print_info(f"can_signal_dict:{VectorCANClass.__can_signal_data_dict}")
            if bool(VectorCANClass.__can_signal_data_dict):
                for key in VectorCANClass.__can_signal_data_dict.keys():
                    robot_print_warning(f"Check can signal, KEY: {key} for message_name: {message_name}, "
                                        f"DIC: {VectorCANClass.__can_signal_data_dict[key]}")
                    robot_print_info(f"{key, message_name}")
                    if key == message_name:

                        if VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_SIGNAL_STATUS] \
                                == VectorCANClass.__CAN_SIGNAL_RUNNING:
                            robot_print_info(f"message_name: {message_name} is already running")
                            return True, VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_TASK_ID]
                        elif VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_SIGNAL_STATUS] \
                                == VectorCANClass.__CAN_SIGNAL_STOP:
                            return False, VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_TASK_ID]
                    if VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_TASK_ID] == message_name:
                        robot_print_warning(f"Check can signal, KEY: {key} for signal: {message_name},"
                                            f"DIC: {VectorCANClass.__can_signal_data_dict[key]}")

                        if VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_SIGNAL_STATUS] \
                                == VectorCANClass.__CAN_SIGNAL_RUNNING:
                            return True, message_name
                        elif VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_SIGNAL_STATUS] \
                                == VectorCANClass.__CAN_SIGNAL_STOP:
                            return False, message_name
            robot_print_debug(f"CAN data dict empty, DICT: {VectorCANClass.__can_signal_data_dict}", True)
            return False, 0
        except Exception as exp:
            robot_print_error(f"Error to check the CAN status, EXCEPTION: {exp}", True)
            return False, 0

    def send_can_signal_periodically(self, can_des: str, database_num: int = 1, signal_type: str = "TX",
                                     periodicity: int = 100) -> can.CyclicSendTaskABC:
        """
        This method is used to send the CAN signal periodically for a give time interval
        :param signal_type: Type of the signal i.e. Master, TX
        :param can_des: CAN description mention in input File
        :param database_num: database number /channel number
        :param periodicity: Periodic time provided by user in Milisecond in case not provided in input file
        :return: Task object if send the signal otherwise False. Result None.
        """
        try:
            can_message_name, message_frame, user_data, db_message = self.__create_can_message(can_des,
                                                                                               database_num=database_num,
                                                                                               signal_type=signal_type)
            if db_message.cycle_time is not None:
                periodic_time = int(db_message.cycle_time) / 1000
                robot_print_info(f"periodic_time:{periodic_time}")
            else:
                robot_print_warning(f"There is not cycle time provided in dbc file for message: {db_message.name}, "
                                    f"So setting cycle time as: {periodicity}ms", print_in_report=True, underline=True)
                periodic_time = int(periodicity) / 1000
            task = None
            # check message contain CRC value
            #is_crc = self.__is_msg_contain_crc(db_message, database_num=database_num, user_data=user_data)
            is_crc = False
            msg_step_count = self.read_input_file_data.get_msg_step_count(can_message_name, database_num=database_num,
                                                                          user_data=user_data)
            if is_crc:
                # send signal in with CRC value and store task id
                task = self.__send_can_crc_signal_modify(db_message=db_message, user_data=user_data,
                                                         periodic_time=periodic_time, data_num=database_num)
                return task
            else:
                if can_message_name not in VectorCANClass.__can_signal_data_dict.keys():
                    if database_num == 1:
                        task = self.can_bus1.send_periodic(message_frame, periodic_time)
                    elif database_num == 2:
                        task = self.can_bus2.send_periodic(message_frame, periodic_time)
                else:
                    task_id = VectorCANClass.__can_signal_data_dict[can_message_name][VectorCANClass.__CAN_TASK_ID]
                    task_id.modify_data(message_frame)
                    return task_id
                if isinstance(task, can.CyclicSendTaskABC):
                    self.__can_record_data(can_message_name, task, signal_type, is_crc)
                    return task
                else:
                    robot_print_warning("None type of CAN signals")
        except can.CanError as can_error:
            robot_print_debug("There is an exception to send the CAN signal periodically, \nException: {can_error}",
                              True)
            robot_print_error(
                "There is an exception to send the CAN signal periodically, \nException: %s" % can_error)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error in {exc_type}, {fname}, {exc_tb.tb_lineno}",
                              print_in_report=True)


    def stop_can_periodically_signal(self, task: can.CyclicSendTaskABC) -> None:
        """
        This method is used to stop the periodic message
        :param task: A can.CyclicSendTask object which to be stopped
        :return:None
        """
        try:
            robot_print_debug(f"Stop call for task: {task}", True)
            # status, can_message_name = self.__check_can_signal_status(task)
            if task is not None:
                task.stop()
                for key in VectorCANClass.__can_signal_data_dict.keys():
                    if VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_TASK_ID] == task:
                        VectorCANClass.__can_signal_data_dict[key][
                            VectorCANClass.__CAN_IS_CRC] = False
                        VectorCANClass.__can_signal_data_dict[key][
                            VectorCANClass.__CAN_SIGNAL_STATUS] = VectorCANClass.__CAN_SIGNAL_STOP
                        robot_print_info(f"in stop with key: {key}, and task : {task}")
                        break
        except can.CanError as can_error:
            robot_print_error(f"There is an exception to stop the CAN periodic signal, \nException: {can_error}")

    def shut_down_can_bus(self, database_num: int = 1) -> None:
        """
        To shout down can bus
        """
        CanBus.shutdown_can_bus(int(database_num))

    def __stop_master_can_signal(self) -> bool:
        """
        This method is used to stop the CAN master signals.
        :return: None
        """
        try:
            robot_print_debug(f"Stopping the CAN signals...", True)
            # Get the data from the global list and stop the Master signals
            for task in VectorCANClass.__master_can_signal_task_list:
                self.stop_can_periodically_signal(task=task)
                robot_print_info(f"Stop CAN signal with task ID: {task}")
            robot_print_debug(f"CAN Master signals stops.", True)
            return True
        except Exception as exp:
            robot_print_error(f"Error to stop the CAN Master signals, EXCEPTION: {exp}")
            return False

    def __stop_pending_running_can_signal(self) -> None:
        """
        This Function will stop running can signal
        :return: None
        """
        try:
            for key in VectorCANClass.__can_signal_data_dict.keys():
                if VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_SIGNAL_STATUS] \
                        == VectorCANClass.__CAN_SIGNAL_RUNNING:
                    task_id = VectorCANClass.__can_signal_data_dict[key][VectorCANClass.__CAN_TASK_ID]
                    robot_print_debug(f"Stopping Pending CAN signal: {key} with task ID: {task_id}", True)
                    self.stop_can_periodically_signal(task=task_id)
        except Exception as exp:
            robot_print_error(f"Error to stop the pending CAN signal, EXCEPTION: {exp}")

    def receive_can_message_data(self, can_des, database_num: int = 1, timeout: float = 10, is_list: bool = True,
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
        try:
            if is_list == is_dict:
                robot_print_warning("Either is_list or is_dict type of data it will return, Both can't be selected"
                                    "List Value by Default it will return in this case!", underline=True)
                is_dict = False
                is_list = True
            can_message = self.read_input_file_data.get_msg_object_by_can_des(can_des=can_des, signal_type="RX",
                                                                              database_num=database_num)
            extended_id = can_message.is_extended_frame
            message = can.Message(arbitration_id=can_message.frame_id, is_extended_id=extended_id, is_rx=True)
            data = None
            if database_num == 1:
                data = self.get_can_trace_ch1.get_message_data(can_message=message, timeout=timeout)
            elif database_num == 2:
                data = self.get_can_trace_ch2.get_message_data(can_message=message, timeout=timeout)
            if is_list:
                return list(data)
            if is_dict:
                return self.read_input_file_data.get_decoded_data(message_name=can_message.name, user_data=data,
                                                                  database_num=database_num)
        except Exception as exp:
            robot_print_error(f" Error in get_can_message_data EXCEPTION:{exp}")

    def start_can_trace(self, database_num: int, interval):
        """
                This method will start collecting the CAN trace for the given interval
                :param interval: log the CAN data based on this interval in seconds
                :param database_num: channel number or database number
        """

        total, used, free = shutil.disk_usage("/")
        free_space = free // (2 ** 30)
        robot_print_info("Total: %d GiB" % (total // (2 ** 30)))
        robot_print_info("Used: %d GiB" % (used // (2 ** 30)))
        robot_print_info("Free: %d GiB" % (free // (2 ** 30)))
        if self.is_interval_can_trace_given:
            if int(free_space) < int(3):
                robot_print_info("The Disk space is not sufficient to store the logging!!!! either disable the "
                                 "canIntervalEnable in can_config_file.json or free up the drive space")

                raise Exception("Insufficient disk space")
            try:
                if database_num == 1:
                    self.get_can_trace_ch1.get_all_trace()
                    robot_print_debug(f"self.is_interval_given:{interval}")
                    sleep(int(interval))

                if database_num == 2:
                    self.get_can_trace_ch2.get_all_trace()
                    robot_print_info(f"self.is_interval_given >>>>>:{interval}")
                    sleep(int(interval))
            except Exception as exp:
                robot_print_error(f" Error to collect get can trace  EXCEPTION:{exp}")
        else:
            robot_print_info("canIntervalEnable is disabled in can_config_file.json")

    def start_time_rotate_logs(self, database_num, when, interval, backup_count):
        """
               This method will start rotate the log file based on the interval
               :param interval: log the CAN data based on this interval
               :param when: It will M for minutes , D for days and S for second
               :param backup_count: number files to be retained after rotate log
               :param database_num: channel number or database number
        """

        total, used, free = shutil.disk_usage("/")
        free_space = free // (2 ** 30)
        robot_print_info("Total: %d GiB" % (total // (2 ** 30)))
        robot_print_info("Used: %d GiB" % (used // (2 ** 30)))
        robot_print_info("Free: %d GiB" % (free // (2 ** 30)))
        if self.is_interval_can_trace_given:
            if int(free_space) < int(3):
                robot_print_info("The Disk space is not sufficient to store the logging!!!! either disable the "
                                 "canIntervalEnable in can_config_file.json or free up the drive space")

                raise Exception("Insufficient disk space")
            try:
                if database_num == 1:
                    self.get_can_trace_ch1.time_rotate_logs(when=when, interval=interval, backup_count=backup_count)

                elif database_num == 2:
                    self.get_can_trace_ch2.time_rotate_logs(when, interval, backup_count)
            except Exception as exp:
                robot_print_error(f" Error to collect get can trace  EXCEPTION:{exp}")
        else:
            robot_print_info("canIntervalEnable is disabled in can_config_file.json")

    def get_rx_message(self, database_num):
        """
                This method will determine whether the RX message was received or not
                :param database_num: channel number or database number
                :return True if RX message received else False
        """

        if database_num == 1:
            msg_var = self.can_bus1.recv(timeout=0.1)
            if msg_var is not None:
                robot_print_info(f"Received Rx from cluster:{msg_var}")
                return True
            else:
                robot_print_info(f"Not receiving any message from cluster")
                return False
        elif database_num == 2:
            msg_var = self.can_bus2.recv(timeout=0.1)
            if msg_var is not None:
                robot_print_info(f"Received Rx from cluster:{msg_var}")
                return True
            else:
                robot_print_info(f"Not receiving any message from cluster")
                return False

    def stop_can_trace(self, data_num: int = 1) -> None:
        """
        This method is used to stop the CAN signals trace.
        :return: None
        """
        if self.is_send_can_master_signal:
            robot_print_debug(f"Stopping Master signals", True)
            if self.__stop_master_can_signal():
                robot_print_debug(f"Stopping CAN Trace signals", True)

        if self.is_start_can_trace:
            robot_print_debug(
                f"Wait...!!! we are checking if there is any pending CAN signal running before stopping the CAN trace",
                True)
            self.__stop_pending_running_can_signal()
            robot_print_debug(f"Wait...!!!Stopping CAN trace", True)
            if data_num == 1:
                self.get_can_trace_ch1.stop_can_trace()
            if data_num == 2:
                self.get_can_trace_ch2.stop_can_trace()
            robot_print_debug(f"CAN signals stop", True)

        elif self.is_interval_can_trace_given:
            robot_print_debug(
                f"Wait...!!! we are checking if there is any pending CAN signal running before stopping the CAN trace",
                True)
            self.__stop_pending_running_can_signal()
            robot_print_debug(f"Wait...!!!Stopping CAN trace", True)
            if data_num == 1:
                robot_print_info(f"data_num:{data_num}")
                self.get_can_trace_ch1.stop_can_trace()
            elif data_num == 2:
                robot_print_info(f"data_num:{data_num}")
                self.get_can_trace_ch2.stop_can_trace()
            robot_print_debug(f"CAN signals stop", True)


class CalculateRcValue:

    def __init__(self, frame: bytearray, rc_len: int, rc_max_value: int, mask: int):
        self.frame = frame[6]
        self.rc_len = rc_len
        self.mask = mask
        self.rc_max_val = rc_max_value - 1
        # robot_print_debug(f"Starting value of RC = {self.frame}, {type(self.frame)}")
        self.rc_value = int(bin(self.frame)[2:].ljust(8, "0")[8 - self.rc_len:], 2)
        # robot_print_debug(f"Starting value of RC = {self.rc_value}")

    def get_rc_next_value(self, frame: bytearray = None, id_msg: int = None):
        if frame is not None:
            self.frame = frame[6]
        if self.rc_value > self.rc_max_val:
            self.rc_value = 0
            # robot_print_debug(f"Resetting the RC value to 0, id msg : {id_msg}")
        self.frame &= self.mask
        self.frame |= self.rc_value
        self.rc_value += 1
        return self.frame


class CanFrameHandler:
    __can_frames = {}

    def __init__(self):
        pass
        # self.lock = threading.Lock()

    def get_can_message_frame(self, message_name) -> bytearray:
        frame = CanFrameHandler.__can_frames[message_name]
        if frame is not None:
            CanFrameHandler.__can_frames[message_name] = None
            return frame

    def set_can_message_frame(self, value: bytearray, message_name):
        CanFrameHandler.__can_frames[message_name] = value
