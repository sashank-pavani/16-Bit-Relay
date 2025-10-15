from typing import Union

from can import Bus
import can
from can.interfaces.vector import VectorBus
# from can.interfaces.pcan import PcanBus
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork import PcanTxLog
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import VECTOR_APP_NAME_LIST, VECTOR_CAN_BUS_TYPE
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PCAN_BUS_TYPE, PCAN_CHANNEL_LIST


class CanBus:
    """
    This class is used to provide CAN bus instances. Its implementation is based on the Singleton class concept.
    """
    _instances = {}

    @staticmethod
    def get_can_bus_instance(bus_type: str, app_name: str, bit_rate: int, channel: int) -> 'Bus':
        """
        This 'static' method is used to provide the CAN bus instance only once (only one instance is shared
        across the execution).
        :param bus_type: Type of bus, e.g. Pcan, Vector, SocketCan etc.
        :param app_name: app_name to be used to handle the CAN interface (CANoe, CANalyzer, etc.).
        :param bit_rate: bit rate of CAN.
        :param channel: Channel in which CAN communicates.
        :return: can.Bus() instance.
        """
        instance_key = (bus_type, app_name, bit_rate, channel)
        if instance_key not in CanBus._instances:
            CanBus._instances[instance_key] = CanBus(bus_type, app_name, bit_rate, channel)._create_instance()
        return CanBus._instances[instance_key]

    def _create_instance(self):
        if self.bus_type.lower() == VECTOR_CAN_BUS_TYPE:
            if self.app_name in VECTOR_APP_NAME_LIST:
                # return VectorBus(channel=[self.channel], app_name=self.app_name, bitrate=self.bit_rate,
                #                  receive_own_messages=True)
                # return VectorBus(channel=[self.channel], app_name=self.app_name, bitrate=self.bit_rate,
                #                  receive_own_messages=True, sample_point=80)
                # return VectorBus(channel=[self.channel], app_name=self.app_name, bitrate=self.bit_rate,
                #                  data_bitrate=2000000, fd=True, receive_own_messages=True)
                 return VectorBus(channel=[self.channel], app_name=self.app_name, bitrate=self.bit_rate,
                                    data_bitrate=2000000, fd=True, receive_own_messages=True ,sjw_abr=8, tseg1_abr=31, tseg2_abr=8, sam_abr=80, sjw_dbr=6, tseg1_dbr=13, tseg2_dbr=6,output_mode=1)

            else:
                raise ValueError(f"Invalid App Name {self.app_name}. Please provide app_name from"
                                 f" {VECTOR_APP_NAME_LIST} in can_config_file.json")
        elif self.bus_type.lower() == PCAN_BUS_TYPE:
            if self.channel in PCAN_CHANNEL_LIST:
                return PcanTxLog.PcanBus(channel=self.channel, bitrate=self.bit_rate, receive_own_messages=True)
            else:
                raise ValueError(f"Invalid channel {self.channel}. Please provide channel from"
                                 f" {PCAN_CHANNEL_LIST} in can_config_file.json")
        else:
            raise ValueError(f"Invalid Bus type {self.bus_type}. Please provide 'busType': 'vector' or PCAN"
                             " in can_config_file.json")

    def __init__(self, bus_type: str, app_name: str, bit_rate: int, channel: int):
        self.bus_type = bus_type.lower()
        self.app_name = app_name
        self.bit_rate = bit_rate
        self.channel = channel

    @staticmethod
    def shutdown_can_bus(database_num: int) -> None:
        """
        To Close the Can bus Instance created!!
        :return: None
        """
        try:
            if CanBus._instances is not None:
                values = list(CanBus._instances.values())
                if database_num == 1:
                    values[0].shutdown()
                    values[0] = None
                    robot_print_info("Successfully shutdown the first can bus")
                elif database_num == 2:

                    values[1].shutdown()
                    values[1] = None
                    robot_print_info("Successfully shutdown the Second can bus")
            CanBus._instances[0] = None
            CanBus._instances[1] = None
        except can.CanError as can_error:
            robot_print_error(f"There is an error to create the CAN bus instance, \nException {can_error}")

    @staticmethod
    def calculate_table_crc() -> Union[bytearray,None]:
        """
        This method is calculated the CRC value and return the checksum.
        This method is used 0x1D (CRC8 SAE J1850) to calculate the CRC value.
        :return:
        """
        try:
            crc_table = [0]*256
            generator = 0x1D
            for divident in range(0, 256):
                currByte = divident
                for bit in range(0, 8):
                    if (currByte & 0x80) != 0:
                        currByte <<= 1
                        currByte ^= generator
                    else:
                        currByte <<= 1
                if currByte < 256:
                    # robot_print_debug(f"currByte :{currByte}")
                    # robot_print_debug(f"divident :{divident}")
                    crc_table[divident] = currByte
            return bytearray(crc_table)
        except Exception as exp:
            robot_print_error(f"Error to calculate the CRC value, EXCEPTION: {exp}")
            return None

    @staticmethod
    def calculate_checksum(data: bytearray, crc_table: bytearray) -> Union[bytearray, None]:
        """
        This method is calculated the CRC value and return the checksum.
        This method is used 0x1D (CRC8 SAE J1850) to calculate the CRC value.
        :param crc_table:
        :param data:
        :return:
        """
        try:
            crc_checksum = 255
            for crc_it in range(7):
                crc_val = data[crc_it] ^ crc_checksum
                crc_checksum = crc_table[crc_val]
            crc_checksum ^= CanBus._CAN_MSG_CRC_BIT_MASK
            return bytearray(crc_checksum)
        except Exception as exp:
            robot_print_error(f"Error to calculate the CRC value, EXCEPTION: {exp}")
            return None
