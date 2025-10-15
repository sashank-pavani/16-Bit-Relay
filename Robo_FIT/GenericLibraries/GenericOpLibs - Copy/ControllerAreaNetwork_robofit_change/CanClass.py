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
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, robot_print_info
from typing import Union


class CanClass(ICan):
    """
    This function call VectorCAN class Methods
    """

    def __init__(self, channel_name):
        self.config_manager = ConfigurationManager()
        self.can_instance: None
        # self.can_instance: VectorCANClass
        self.__initialize_can(channel_name)

    def __initialize_can(self, channel_name):
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
        robot_print_info(f"i got called here")
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

    def process_hex_to_bin(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 4:
            print("The task does not have an index 4.")
            return None

        # Print the entire task array to check its contents
        robot_print_info(f"Task array: {task}")

        # Get the value at index 4
        hex_value = task[6]

        # Print the value at index 4
        robot_print_info(f"Value at task[6]: {hex_value}")

        # Ensure hex_value is a string
        if not isinstance(hex_value, str):
            hex_value = str(hex_value)

        try:
            # Convert hex_value to an integer
            int_value = int(hex_value, 16)
            # Print the integer value
            print(f"Converted integer value: {int_value}")
        except ValueError as e:
            print(f"Error converting {hex_value} to an integer: {e}")
            return None

        # Convert the integer to a binary string
        bin_value = f"{int_value:08b}"
        # Print the binary value
        robot_print_info(f"Binary Value: {bin_value}")

        return bin_value

    def relay_on_check(self, task):
        bin_value = self.process_hex_to_bin(task)
        if bin_value is None:
            return
        if bin_value[:2] == '00':
            robot_print_info("Relay On Check: Pass")
        else:
            robot_print_info("Relay On Check: Fail")

    def relay_off_check(self, task):
        bin_value = self.process_hex_to_bin(task)
        if bin_value is None:
            return
        if bin_value[:2] == '01':
            robot_print_info("Relay Off Check: Pass")
        else:
            robot_print_info("Relay Off Check: Fail")

    def hvil_close(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 6:
            print("The task does not have an index 6.")
            return False

        hex_value = task[6]
        # Print the value and its type
        robot_print_info(f"Value at task[6]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '00':
            robot_print_info("hvil close check: Pass")
            return True
        else:
            robot_print_error("hvil close check: Fail")
            return False

    def hvil_open(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 6:
            print("The task does not have an index 6.")
            return False

        hex_value = task[6]
        # Print the value and its type
        robot_print_info(f"Value at task[6]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '01':
            robot_print_info("hvil open Check: Pass")
            return True
        else:
            robot_print_error("hvil open Check: Fail")
            return False

    def service_disconnect_close(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 2:
            print("The task does not have an index 3.")
            return False

        hex_value = task[4]
        # Print the value and its type
        robot_print_info(f"Value at task[4]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '00':
            robot_print_info("service disconnect close check: Pass")
            return True
        else:
            robot_print_error("service disconnect close check: Fail")
            return False

    def service_disconnect_error(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 3:
            print("The task does not have an index 3.")
            return False

        hex_value = task[4]
        # Print the value and its type
        robot_print_info(f"Value at task[4]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '10':
            robot_print_info("service disconnect close check: Pass")
            return True
        else:
            robot_print_error("service disconnect close check: Fail")
            return False

    def service_disconnect_open(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 3:
            print("The task does not have an index 3.")
            return False

        hex_value = task[4]
        # Print the value and its type
        robot_print_info(f"Value at task[4]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '01':
            robot_print_info("service disconnect open check: Pass")
            return True
        else:
            robot_print_error("service disconnect open check: Fail")
            return False

    def DC_EO_HVL_init(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 2:
            print("The task does not have an index 3.")
            return False

        hex_value = task[3]
        # Print the value and its type
        robot_print_info(f"Value at task[3]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '00':
            robot_print_info("DC init check: Pass")
            return True
        else:
            robot_print_error("DC init check: Fail")
            return False

    def DC_EO_HVL_precharge(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 2:
            print("The task does not have an index 3.")
            return False

        hex_value = task[3]
        # Print the value and its type
        robot_print_info(f"Value at task[3]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] != '00':
            robot_print_info("DC precharge check: Pass")
            return True
        else:
            robot_print_error("DC precharge check: Fail")
            return False

    def DC_EO_HVL_Greater_Volt(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 2:
            print("The task does not have an index 3.")
            return False

        hex_value = task[3]
        # Print the value and its type
        robot_print_info(f"Value at task[3]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '10':
            robot_print_info("DC greater voltage check: Pass")
            return True
        else:
            robot_print_error("DC greater voltage: Fail")
            return False

    def DC_EO_HVL_lesser_Volt(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 2:
            print("The task does not have an index 3.")
            return False

        hex_value = task[3]
        # Print the value and its type
        robot_print_info(f"Value at task[3]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")

        if bin_value[:2] == '01':
            robot_print_info("DC lesser voltage check: Pass")
            return True
        else:
            robot_print_error("DC lesser voltage check: Fail")
            return False

    def BMC_bank_status(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 1:
            print("The task does not have an index 1.")
            return False

        hex_value = task[1]
        # Print the value and its type
        robot_print_info(f"Value at task[1]: {hex_value}, Type: {type(hex_value)}")

        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")
        first_four_bits = bin_value[:4]
        decimal_value = int(first_four_bits, 2)
        robot_print_info(f"decimal value is : {decimal_value} ")
        robot_print_info(f"First four bits in binary: {first_four_bits}, Decimal: {decimal_value}")
        return str(decimal_value)

    def BMC_modus_status(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")
        if len(task) <= 4:
            print("The task does not have an index 1.")
            return False
        hex_value = task[4]
        robot_print_info(f"Value at task[4]: {hex_value}, Type: {type(hex_value)}")
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False
        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")
        last_four_bits = bin_value[-4:]
        decimal_value = int(last_four_bits, 2)
        robot_print_info(f"Decimal value of last four bits: {decimal_value}")
        robot_print_info(f"Last four bits in binary: {last_four_bits}, Decimal: {decimal_value}")
        return str(decimal_value)

    def BMC_modus_status1(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")

        if len(task) <= 4:
            print("The task does not have an index 4.")
            return False

        hex_value = task[4]
        # Print the value and its type
        robot_print_info(f"Value at task[4]: {hex_value}, Type: {type(hex_value)}")

        # Ensure hex_value is a string or convert it if possible
        if not isinstance(hex_value, str):
            if isinstance(hex_value, (int, bytes)):
                hex_value = hex(hex_value)[2:]  # Convert to hex string, removing '0x'
            else:
                print(f"Unsupported type for hex_value: {type(hex_value)}")
                return False

        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"
        robot_print_info(f"Binary Value: {bin_value}")
        sub_bits = bin_value[4:8]
        # Convert sub_bits to a number
        sub_bits_number = int(sub_bits, 2)

        # Extract the last 4 bits
        last_4_bits = sub_bits_number & 0xF  # Masking to get the last 4 bits

        # Convert the last 4 bits to hexadecimal
        last_4_bits_hex = hex(last_4_bits)[2:].upper()  # Remove '0x' and convert to uppercase

        # robot_print_info(f"Last 4 Bits in Hexadecimal: {last_4_bits_hex}")
        target = '0001'

        # if sub_bits == target:
        #     robot_print_info("safe state triggered : Pass")
        #     return True
        # else:
        #     robot_print_error("safe state didn't triggered: Fail")
        #     return False

        if last_4_bits_hex == '1':
            robot_print_info("Safe state triggered: Pass")
            robot_print_info(f"BMC_Modus value is : {last_4_bits_hex}")
            return True
        else:
            robot_print_error("Safe state didn't trigger: Fail")
            robot_print_error(f"BMC_Modus value is : {last_4_bits_hex}")
            return False

    def ISO_POS_INIT(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a bytearray.")

        if len(task) < 24:
            print("The bytearray does not have 23 and 24 bytes.")
            return False

        # Read the 23rd and 24th bytes
        byte_23 = task[22]
        byte_24 = task[23]

        # Convert to hex strings
        hex_byte_23 = f"{byte_23:02x}"
        hex_byte_24 = f"{byte_24:02x}"

        # Combine the two hex values
        combined_hex = f"{hex_byte_23}{hex_byte_24}"

        # Print the combined hex values
        robot_print_info(f"23rd and 24th byte: {combined_hex}")

        # Check if the combined value is 'fdff' or '0000'
        if combined_hex == 'fdff' or combined_hex == '0000':
            robot_print_info("Check passed.")
            return True
        else:
            robot_print_error("Check failed.")
            return False


    def ISO_NEG_INIT(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a bytearray.")

        if len(task) < 24:
            print("The bytearray does not have 23 and 24 bytes.")
            return False

        # Read the 23rd and 24th bytes
        byte_21 = task[20]
        byte_22 = task[21]

        # Convert to hex strings
        hex_byte_21 = f"{byte_21:02x}"
        hex_byte_22 = f"{byte_22:02x}"

        # Combine the two hex values
        combined_hex = f"{hex_byte_21}{hex_byte_22}"

        # Print the combined hex values
        robot_print_info(f"21st and 22nd byte: {combined_hex}")

        # Check if the combined value is 'fdff' or '0000'
        if combined_hex == 'fdff' or combined_hex == '0000':
            robot_print_info("Check passed.")
            return True
        else:
            robot_print_error("Check failed.")
            return False


    def ISO_POS(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a bytearray.")

        if len(task) < 24:
            print("The bytearray does not have 23 and 24 bytes.")
            return False

        # Read the 23rd and 24th bytes
        byte_23 = task[22]
        byte_24 = task[23]

        # Convert to hex strings
        hex_byte_23 = f"{byte_23:02x}"
        hex_byte_24 = f"{byte_24:02x}"

        # Combine the two hex values
        combined_hex = f"{hex_byte_23}{hex_byte_24}"

        # Print the combined hex values
        robot_print_info(f"23rd and 24th byte: {combined_hex}")

        # Check if the combined value is 'fdff' or '0000'
        if combined_hex != 'fdff':
            # and combined_hex != '0000'
            robot_print_info("Check passed.")
            return True
        else:
            robot_print_error("Check failed.")
            return False

    def ISO_NEG(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a bytearray.")

        if len(task) < 24:
            print("The bytearray does not have 23 and 24 bytes.")
            return False

        # Read the 23rd and 24th bytes
        byte_21 = task[20]
        byte_22 = task[21]

        # Convert to hex strings
        hex_byte_21 = f"{byte_21:02x}"
        hex_byte_22 = f"{byte_22:02x}"

        # Combine the two hex values
        combined_hex = f"{hex_byte_21}{hex_byte_22}"

        # Print the combined hex values
        robot_print_info(f"21st and 22nd byte: {combined_hex}")

        # Check if the combined value is 'fdff' or '0000'
        if combined_hex != 'fdff':
            # and combined_hex != '0000'
            robot_print_info("Check passed.")
            return True
        else:
            robot_print_error("Check failed.")
            return False

    def ISO_IWU_STATUS(self, task: can.CyclicSendTaskABC):
        if not isinstance(task, list):
            raise TypeError("The task should be a list of hexadecimal values.")
        if len(task) <= 18:
            print("The task does not have an index 16.")
            return False

        hex_value = task[16]
        robot_print_info(f"Value at task[16]: {hex_value}, Type: {type(hex_value)}")

        # Convert hex_value to string if it's an int or bytes
        if isinstance(hex_value, int):
            hex_value = f"{hex_value:02x}"  # Convert int to 2-digit hex string (e.g., 4 becomes '04')
        elif isinstance(hex_value, bytes):
            hex_value = hex_value.hex()
        elif not isinstance(hex_value, str):
            print(f"Unsupported type for hex_value: {type(hex_value)}")
            return False

        robot_print_info(f"Hexadecimal Value (as string): {hex_value}")

        # Convert the hexadecimal string to an integer, then to an 8-bit binary string
        int_value = int(hex_value, 16)
        bin_value = f"{int_value:08b}"  # Convert to binary and zero-fill to 8 bits
        robot_print_info(f"Binary Value: {bin_value}")

        # Extract bits 3, 4, and 5 (from the right)
        selected_bits = bin_value[-5:-2]  # Slices the binary string to get bits 3, 4, and 5
        robot_print_info(f"Selected bits (3, 4, 5 from the right): {selected_bits}")

        # Convert the selected bits from binary to decimal
        decimal_value = int(selected_bits, 2)
        robot_print_info(f"Decimal Value of selected bits (as integer): {decimal_value}")

        # Return or print the decimal value as a string
        return str(decimal_value)

    def ISO_BMC_IWU(self, task: can.CyclicSendTaskABC):
        # Ensure the task is a list
        if not isinstance(task, list):
            raise TypeError("The task should be a list.")

        # Print the entire task (list)
        robot_print_info("Received task (list):", task)





