import re
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, CRE_LIBRARIES, \
    CRE_EXTERNAL_FILES, CRE_DB_FILES, CRE_INPUT_FILES, ROBO_CAN_INPUT_FILE_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfiguratorReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from isotp import AddressingMode


class ConfigurationManager:
    """
    This class is for CAN->to manage configuration
    """

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()
        self.config_reader = ConfiguratorReader()

    def get_bus_type(self) -> str:
        """
        This method is used to read the bus_type from configuration file
        :return: bus type as string
        """
        return self.config_reader.read_string("busType")

    def get_app_name(self) -> str:
        """
        This method is used to read the app name from configuration file
        :return: app name as string
        """
        return self.config_reader.read_string("appName")

    def get_bit_rate(self, device: str) -> int:
        """
        This method is used to read the bit rate from the configuration file.
        :param device : channel_name dual or single
        :return: bit rate in Integer
        """

        channel_list = self.config_reader.read_list("channels")
        for data in channel_list:
            if device.lower() == data["channelName"]:
                return int(data["bitRate"])
        raise ValueError("It seems bitRate is not provided in can_config_file.json.")

    def get_channel(self, device: str) -> int:
        """
        This method is used to read the channel name from the configuration file.
        :param device : channel_name dual or single
        :return: Channel value as string
        """

        channel_list = self.config_reader.read_list("channels")
        for data in channel_list:
            if device.lower() == data["channelName"]:
                return data["channel"]
        raise ValueError("It seems channel is not provided in can_config_file.json.")

    def get_can_input_file_path(self) -> str:
        """
        This method is used to read logger file path from the configuration file
        :return: CAN logger file path as String
        """
        try:
            can_input_file_name = self.config_reader.read_string("canInputFileName")
            if can_input_file_name == "":
                input_file_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, CRE_LIBRARIES,
                                               CRE_EXTERNAL_FILES, CRE_INPUT_FILES, ROBO_CAN_INPUT_FILE_NAME)
                return input_file_path
            else:
                input_file_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, CRE_LIBRARIES,
                                               CRE_EXTERNAL_FILES, CRE_INPUT_FILES, can_input_file_name)
                if os.path.isfile(input_file_path):
                    return input_file_path
                else:
                    raise FileNotFoundError(f"File not found at path :{input_file_path}")
        except TypeError:
            robot_print_error("'canInputFileName' Key not present in can_config_file.json")
            robot_print_warning(f"Key canInputFileName is not define in can_config_file.json so,we are using default"
                                f" '{ROBO_CAN_INPUT_FILE_NAME}'")
            input_file_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, CRE_LIBRARIES,
                                           CRE_EXTERNAL_FILES, CRE_INPUT_FILES, ROBO_CAN_INPUT_FILE_NAME)
            return input_file_path
        except Exception as exp:
            robot_print_error(f"Error to get_can_input_file_path EXCEPTION:{exp}")

    def get_can_trace_file_name_ch(self, device) -> str:
        """
        This method is used to read logger file path from the configuration file
        :param device : channel_name dual or single
        :return: CAN logger file path as String
        """

        channel_list = self.config_reader.read_list("channels")
        for data in channel_list:
            if device.lower() == data["channelName"]:
                return data["canTraceFile"]
        raise ValueError("It seems canTraceFile is not provided in can_config_file.json.")

    def get_can_trace_file_path(self, file_name: str) -> str:
        return os.path.join(self.common_keyword.get_can_trace_dir(), file_name)

    def get_can_db_file_path_ch(self, device) -> str:
        """
        This method is used to read Database file path from the configuration file
        :param device : channel_name dual or single
        :return: CAN database file path as String
        """

        try:
            channel_list = self.config_reader.read_list("channels")
            for data in channel_list:
                if device.lower() == data["channelName"]:
                    can_db_file_name = data["canDbcFile"]
                    can_db_file_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, CRE_LIBRARIES,
                                                    CRE_EXTERNAL_FILES, CRE_DB_FILES, can_db_file_name)
                    robot_print_info(f"CAN DB file path is : {can_db_file_path}")
                    return can_db_file_path
        except Exception as exp:
            robot_print_error(f"Error to get the db file path check EXCEPTION:{exp}")

    def get_can_trace_enable(self) -> bool:
        """
        This method return the True of false base of user configuration.
        If user set 'canTraceEnable' is true then it return true otherwise false
        :return: Bool value
        """
        value = self.config_reader.read_string("canTraceEnable")
        if value.lower() == "true":
            return True
        else:
            return False

    def get_interval_trace_enable(self) -> bool:
        """
        This method return the True of false base of user configuration.
        If user set 'canIntervalEnable' is true then it return true otherwise false
        :return: Bool value
        """
        value = self.config_reader.read_string("canIntervalEnable")
        if value.lower() == "true":
            return True
        else:
            return False

    def get_master_signal_status(self) -> bool:
        try:
            value = self.config_reader.read_string("isSendCanMasterSignal")
            if value.lower() == "true":
                return True
            else:
                return False
        except Exception as exp:
            print(f"Error to get the status of CAN master signals. EXCEPTION: {exp}")
            return False

    # uds on can dict read
    def get_req_id(self) -> int:
        """
        This Function use to get value of key 'reqId' from can_config_file.json in string format
        """
        try:
            uds_dict = self.config_reader.read_list("uds")
            reqId = uds_dict["reqId"]
            match = re.match(r'0x[\dA-F]{3}', reqId)
            if match is not None:
                return int(reqId, 16)
            else:
                robot_print_error("Please Provide Valid Request Id!!")
        except Exception as exp:
            robot_print_error(f"Error to get_req_id EXCEPTION: {exp}")

    def get_res_id(self) -> int:
        """
        This Function use to get value of key 'resId' from can_config_file.json in string format
        """
        try:
            uds_dict = self.config_reader.read_list("uds")
            resId = uds_dict["resId"]
            match = re.match(r'0x[\dA-F]{3}', resId)
            if match is not None:
                return int(resId, 16)
            else:
                robot_print_error("Please Provide Valid Request Id!!")
        except Exception as exp:
            robot_print_error(f"Error to get_res_id EXCEPTION: {exp}")

    def get_address_mode_old(self) -> int:
        """
        This Function use to get value of keys available in addressing_mode dict keys from
        can_config_file.json inint format
        """
        try:
            uds_dict = self.config_reader.read_list("uds")
            addressing_modes_dict = {"Normal_11bits": 0, "Normal_29bits": 1, "NormalFixed_29bits": 2,
                                     "Extended_11bits": 3,
                                     "Extended_29bits": 4, "Mixed_11bits": 5, "Mixed_29bits": 6}
            addr_mode = uds_dict["addressing_mode"]
            if addr_mode in addressing_modes_dict:
                return int(addressing_modes_dict[addr_mode])
            else:
                robot_print_error(f"Please Provide Valid Addressing Mode: {addressing_modes_dict.keys()}")
        except Exception as exp:
            robot_print_error(f"Error to get_address_mode EXCEPTION: {exp}")

    def get_address_mode(self) -> AddressingMode:
        """
            This function returns the addressing mode as an AddressingMode enum.
            """
        try:
            uds_dict = self.config_reader.read_list("uds")
            addressing_modes_dict = {
                "Normal_11bits": AddressingMode.Normal_11bits,
                "Normal_29bits": AddressingMode.Normal_29bits,
                "NormalFixed_29bits": AddressingMode.NormalFixed_29bits,
                "Extended_11bits": AddressingMode.Extended_11bits,
                "Extended_29bits": AddressingMode.Extended_29bits,
                "Mixed_11bits": AddressingMode.Mixed_11bits,
                "Mixed_29bits": AddressingMode.Mixed_29bits
            }
            addr_mode = uds_dict["addressing_mode"]
            if addr_mode in addressing_modes_dict:
                return addressing_modes_dict[addr_mode]
            else:
                robot_print_error(f"Please Provide Valid Addressing Mode: {addressing_modes_dict.keys()}")
        except Exception as exp:
            robot_print_error(f"Error in get_address_mode EXCEPTION: {exp}")

    def get_isotp_params(self) -> dict:
        """
        This Function use to get value of key 'isotp_params' from can_config_file.json
        complete dictionary
        # Refer to isotp documentation for full details about parameters
            isotp_params = {
            'stmin': 32,
            # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values
            from 0xF1-0xF9
            'blocksize': 8,  # Request the sender to send 8 consecutives frames before sending a new flow
            control message
            'wftmax': 0,  # Number of wait frame allowed before triggering an error
            'tx_data_length': 8,  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
            'tx_data_min_length': None,
            # Minimum length of CAN messages. When different from None, messages are padded to meet this length.
            Works with CAN 2.0 and CAN FD.
            'tx_padding': 0,  # Will pad all transmitted CAN messages with byte 0x00.
            'rx_flowcontrol_timeout': 1000,  # Triggers a timeout if a flow control is awaited for more than
            1000 milliseconds
            'rx_consecutive_frame_timeout': 1000,
            # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
            'squash_stmin_requirement': False,
            # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
            'max_frame_size': 4095  # Limit the size of receive frame.
            }
        """
        try:
            uds_dict = self.config_reader.read_list("uds")
            iso_params = uds_dict['isotp_params']
            iso_params['tx_data_min_length'] = None
            return iso_params
        except KeyError as key_error:
            robot_print_error(f"Please Provide Valid key :{key_error}")

    def get_config_dict(self) -> dict:
        """
        This Function is used in udsoncan for over write on default config values.



        standard_version(int):The standard version to use, valid values are : 2006, 2013, 2020. [Default value is 2020]



        request_timeout(float):Maximum amount of time in seconds to wait for a response of any kind, positive or
                                negative, after sending a request. After this time is elapsed, a TimeoutException
                                will be raised regardless of other timeouts value or previous client responses.
                                In particular even if the server requests that the client wait, by returning response
                                requestCorrectlyReceived-ResponsePending (0x78), this timeout will still trigger.
                                If you wish to disable this behaviour and have your server wait for as long as it takes
                                for the ECU to finish whatever activity you have requested, set this value to None.
                                [Default value of 5]
        p2_timeout(float):Maximum amount of time in seconds to wait for a first response (positive, negative,
                         or NRC 0x78). After this time is elapsed, a TimeoutException will be raised if
                         no response has been received.See ISO 14229-2:2013 (UDS Session Layer Services) for more
                        details. [Default value of 1]
        p2_star_timeout(float):Maximum amount of time in seconds to wait for a response (positive, negative, or NRC0x78)
                              reception of a negative response with code 0x78 (requestCorrectlyReceived-ResponsePending)
                              After this time is elapsed, a TimeoutException will be raised if no response has been
                              received.See ISO 14229-2:2013 (UDS Session Layer Services) for more details.
                              [Default value of 5]
        use_server_timing:((bool): If True ->  value received from the server will be used
                           If False -> these timing values will be ignored and local configuration timing will be used
                           Note:no timeout value can exceed the config['request_timeout']it is meant to avoid
                                the client from hanging for too long.
                           This parameter has no effect when config['standard_version'] is set to 2006.
        """
        try:
            uds_dict = self.config_reader.read_list("uds")
            config = uds_dict['config']
            return config
        except KeyError as key_error:
            robot_print_error(f"Please Provide Valid key :{key_error}")
