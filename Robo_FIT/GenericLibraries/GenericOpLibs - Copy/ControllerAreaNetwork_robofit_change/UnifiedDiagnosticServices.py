import os
import sys
from typing import Union
from udsoncan.exceptions import ConfigError, NegativeResponseException, \
    InvalidResponseException, UnexpectedResponseException, TimeoutException
import isotp
import udsoncan
import udsoncan.configs
from udsoncan import DidCodec
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
from can.interfaces.vector import VectorBus
from udsoncan.services import ReadDTCInformation

from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_info, robot_print_warning
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import DEFAULT_OPTIONS, SECURITY_LEVELS, \
    IO_CONTROL_PARAM
import struct
from can import Logger
import concurrent.futures
import can
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.CANInputFileParsing.CanInputFileParsing import \
    CanInputFileParsing
from datetime import datetime


class UnifiedDiagnosticServices:
    """
        This class is used for Diagnostic Services
    """

    def __init__(self):
        """
        This Constructor is used for initializing CAN IsoTp Connection for Diagnostic Services and ConfigurationManager
        class initialization for method to call which already defined.
        """
        try:
            self.config_manager = ConfigurationManager()
            self.bus = self.__create_can_bus_instance()  # Link Layer (CAN protocol)
            self.tp_addr = self.__create_network_layer_addressing_scheme()  # Network layer addressing scheme
            self.stack = self.__create_isotp_protocol_instance()  # Network/Transport layer (IsoTP protocol)
            # Interface between Application and Transport layer
            self.connection = self.__create_connection_application_and_transport_layer()
            self.config = dict(udsoncan.configs.default_client_config)  # Create Default Config
            # UDS config parameter override as per project need like; (p2_timeout,p2*_timeout)
            self.config = self.__overwrite_config_params()
            # robot_print_debug( f"Config: {self.config}")
            self.is_trace = True  # Flag to close trace started
            self.is_future = False
            self.future_obj = None
            udsoncan.setup_logging()
        except AttributeError as attr_error:
            robot_print_error(f"Object Attribute or Object is not Valid , EXCEPTION  :{attr_error}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")
        except ValueError as val_error:
            robot_print_error(f"Invalid Argument :{val_error}")
        except Exception as exp:
            robot_print_error(f"Error in UDS Constructor , EXCEPTION:{exp}")

    def __create_logger_instance(self):
        """
        This Function Create Instance of CAN Logger()
        :return: logger instance
        """
        try:
            file_name = 'can_uds_log_' + str(datetime.now().strftime("%d_%m_%Y_%H_%M_%S")) + '_file.asc'
            config_path = self.config_manager.get_can_trace_file_path(file_name)
            return Logger(config_path)
        except Exception as exp:
            robot_print_error(f"Error to create logger instance , EXCEPTION:{exp}")

    def __create_can_input_parsing_instance(self):
        """
        This Function Create Instance of CanInputFileParsing()
        :return: can input XL File Instance
        """
        try:
            read_input_file_data = CanInputFileParsing("single")
            return read_input_file_data
        except Exception as exp:
            robot_print_error(f"Error to create can input xl instance, EXCEPTION: {exp}")

    def __create_can_message(self, can_des: str, database_num: int) -> Union[tuple, None]:
        """
        This mehtod is used to create the CAN message. It read the message form the InputFile.
        :param can_des: CAN description mention in InputFile
        :return: required values in function start_uds_can_signal_periodically
        """
        try:
            read_input_file_data = self.__create_can_input_parsing_instance()
            print(read_input_file_data)
            if read_input_file_data is not None:
                message_name = read_input_file_data.get_can_message_name(can_des=can_des, database_num=database_num)
                print(message_name)
                if message_name is not None:
                    can_message = read_input_file_data.get_msg_object_by_msg_name(
                        message_name=message_name, database_num=database_num)  # dbc_message
                    user_data = read_input_file_data.get_can_data(can_des=can_des, database_num=database_num)
                    extended_id = can_message.is_extended_frame
                    message_frame = can.Message(arbitration_id=can_message.frame_id, data=user_data,
                                                is_extended_id=extended_id, is_rx=False)
                    periodic_duration = int(can_message.cycle_time) / 1000
                    return can_message, message_frame, periodic_duration
                else:
                    raise Exception(f"Message_Name for CAN_DES:{can_des} not found!")
            else:
                raise Exception("CanInputFileParsing Instance Not created !")
        except can.CanError as can_error:
            robot_print_error(f"There is an exception to create CAN message,\nException: {can_error}")
            return None
        except Exception as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def start_uds_can_signal_periodically(self, can_des: str, database_num: int):
        """
        This Function is use to start CAN signal periodically
        NOTE: Don't start can signals periodically from VectorCANClass otherwise it will not allow you to communicate
        in UDS
        :param can_des:(str) CAN Message Name from column CAN_DES mentioned in CAN_input.xlsx file
        :param database_num:(int)data_base number or channel number in int
        """
        try:
            message, message_frame, periodic_duration = self.__create_can_message(can_des, database_num=database_num)
            robot_print_debug(f"{'-' * 20}Sending Message{message.name} with periodicity periodic_duration {'-' * 20}",
                              print_in_report=True)
            self.bus.send_periodic(message_frame, period=periodic_duration)
            robot_print_info(f"{'-' * 20}STARTED CAN SIGNALS PERIODICALLY{'-' * 20}")
        except Exception as exp:
            robot_print_error(f"Error to start uds can signal periodically , EXCEPTION:${exp}")

    def stop_all_uds_can_periodic_signals(self):
        """
        This Function stop all periodic CAN signals
        """
        try:
            self.bus.stop_all_periodic_tasks()
            self.is_future = False
            robot_print_info(f"{'-' * 20}STOPPED ALL PERIODIC CAN SIGNALS {'-' * 20}")
        except Exception as exp:
            self.is_future = False
            robot_print_error(f"Error to stop all uds can periodic signals , EXCEPTION:${exp}")

    def start_uds_can_trace(self):
        """
        This Function is use to start can signal Traces
        """
        try:
            thread_obj = concurrent.futures.ThreadPoolExecutor()
            self.future_obj = thread_obj.submit(self.__get_trace)
            self.is_future = True
            robot_print_info(f"{'-' * 20}STARTED CAN TRACE{'-' * 20}")
        except Exception as exp:
            self.is_trace = False
            self.is_future = False
            robot_print_error(f"Error to start uds can trace , EXCEPTION:${exp}")

    def stop_uds_can_trace(self):
        """
        This Function is used for stop can trace of uds
        """
        try:
            self.is_trace = False
            if not self.is_future:
                self.future_obj.cancel()
                robot_print_info(f"{'-' * 20}STOPPED CAN TRACE{'-' * 20}")
        except Exception as exp:
            self.is_trace = False
            robot_print_error(f"Error to stop uds can trace , EXCEPTION:${exp}")

    def __get_trace(self):
        """
        This Function is use for create Logger Instance and start capturing CAN logs.
        """
        try:
            self.logger = self.__create_logger_instance()  # UDS can logging instance
            self.bus_obj = self.__create_can_bus_instance()
            while self.is_trace:
                msg = self.bus_obj.recv(1)
                if msg is not None:
                    self.logger(msg)
            robot_print_info(f"{'-' * 20}LOGGER INSTANCE CREATED{'-' * 20}")
        except Exception as exp:
            robot_print_error(f"Error to get trace , EXCEPTION:${exp}")
        finally:
            self.is_future = False
            self.bus_obj.shutdown()
            self.is_trace = False
            self.logger.stop()

    def __create_can_bus_instance(self) -> can.interfaces.vector.VectorBus:
        """
        This Function Create and Return CAN Bus Instance
        :return: can bus instance
        """
        try:
            app_name = self.config_manager.get_app_name()
            bit_rate = self.config_manager.get_bit_rate("single")
            channel = self.config_manager.get_channel("single")
            # bus = VectorBus(channel=[channel], bitrate=bit_rate, app_name=app_name, receive_own_messages=True)
            bus = VectorBus(channel=[channel], app_name=app_name, bitrate=bit_rate,
                            data_bitrate=2000000, fd=True, receive_own_messages=True, sjw_abr=32, tseg1_abr=127,
                            tseg2_abr=32,
                            sam_abr=1, sjw_dbr=12, tseg1_dbr=27, tseg2_dbr=12, output_mode=1)
            robot_print_debug("CAN BUS INSTANCE STARTED")
            return bus
        except can.CanError as can_error:
            self.can_bus = None
            robot_print_error(f"There is error to create CAN Bus, Exception:{can_error}")
            sys.exit()
        except Exception as exp:
            robot_print_error(f"Error to create the CAN bus Instance, EXCEPTION: {exp}")

    def __create_network_layer_addressing_scheme(self) -> object:
        """
        This Function Create Network layer addressing scheme Instance and Return Transport Layer Address Instance
        :return: Transport Layer Address Instance
        """
        try:
            self.address_mode = self.config_manager.get_address_mode()
            self.txid = self.config_manager.get_req_id()
            self.rx_id = self.config_manager.get_res_id()
            tp_addr = isotp.Address(self.address_mode, txid=self.txid, rxid=self.rx_id)
            robot_print_debug(f"TP Address: {tp_addr}")
            return tp_addr
        except Exception as exp:
            robot_print_error(f"Error to create network layer addressing scheme, EXCEPTION: {exp}")

    def __create_isotp_protocol_instance(self) -> object:
        """
        This Function Create Network/Transport layer (IsoTP protocol) Instance and Return IsoTP Instance
        :return: IsoTP Instance
        """
        try:
            self.isotp_params = self.config_manager.get_isotp_params()
            robot_print_debug(f"IsoTp Prams: {self.isotp_params}")
            stack = isotp.CanStack(bus=self.bus, address=self.tp_addr, params=self.isotp_params)
            robot_print_debug(f"Stack: {stack}")
            return stack
        except Exception as exp:
            robot_print_error(f"Error to create network layer addressing scheme, EXCEPTION: {exp}")

    def __create_connection_application_and_transport_layer(self) -> object:
        """
        This Function Create interface between Application and Transport layer Instance and Return Connection Instance
        :return: Connection Instance
        """
        try:
            connection = PythonIsoTpConnection(self.stack)
            robot_print_debug(f"Connection: {connection}")
            robot_print_debug(f"{'-' * 20}UDS on CAN Connection Established {'-' * 20}", print_in_report=True)
            return connection
        except Exception as exp:
            robot_print_error(f"Error to create connection of application and transport layer, EXCEPTION: {exp}")

    def __overwrite_config_params(self) -> dict:
        """
        This Function Overwrite and Return complete config dictionary
        :return: config dictionary
        """
        try:
            config = self.config_manager.get_config_dict()
            for key, value in config.items():
                self.config[key] = value
            return self.config
        except Exception as exp:
            robot_print_error(f"Error to overwrite config, EXCEPTION: {exp}")

    # def __create_response(self, resp) -> dict:
    #     """
    #     This Function Create Response of Dictionary and Return Response Dictionary in Format
    #     Example: response = {"service_name": "", "responseCode": 0, "codeName": "", "data": []}
    #     :return: (dict) built response dictionary
    #     """
    #     try:
    #         response = {"service_name": "", "responseCode": 0, "codeName": "", "data": []}
    #         if resp is not None:
    #             try:
    #                 response["service_name"] = resp.service.get_name()
    #             except:
    #                 response["service_name"] = ""
    #             try:
    #                 response["responseCode"] = resp.code
    #             except:
    #                 response["responseCode"] = None
    #             try:
    #                 response["codeName"] = resp.code_name
    #             except:
    #                 response["codeName"] = ""
    #             try:
    #                 response["data"] = resp.service_data.values
    #             except:
    #                 response["data"] = []
    #         robot_print_info(f"Response is : {response}")
    #         return response
    #     except Exception as exp:
    #         robot_print_error(f"Error to crate response Dict, EXCEPTION:{exp}")

    def __create_response(self, resp) -> dict:
        """
        This Function Create Response of Dictionary and Return Response Dictionary in Format
        Example: response = {"service_name": "", "responseCode": 0, "codeName": "", "data": []}
        :return: (dict) built response dictionary
        """
        try:
            response = {"service_name": "", "responseCode": 0, "codeName": "", "data": []}
            if resp is not None:
                try:
                    response["service_name"] = resp.service.get_name()
                except:
                    response["service_name"] = ""
                try:
                    response["responseCode"] = resp.code
                except:
                    response["responseCode"] = None
                try:
                    response["codeName"] = resp.code_name
                except:
                    response["codeName"] = ""
                try:
                    response["data"] = resp.service_data.values
                except:
                    response["data"] = []
            robot_print_info(f"Response is : {response}")
            return response
        except Exception as exp:
            robot_print_error(f"Error to crate response Dict, EXCEPTION:{exp}")
    def __create_data_identifiers(self, did_dict: dict, convert_to: str) -> tuple:
        """
        This Function is use for Create Data Identifier
        :param did_dict:
        Syntax Example : did_dict = {DID_ID: DID_DataLength_Code}
                        Let's take example of Diagnostic Session Check DID 0xF186 which return 1 byte of data so your
                        did_dict = {0xF186 : 1}
        :param convert_to: Data you want to covert to should be from ["hex_list","ascii","int_list"]
        :return: (tuple) data_identifiers will return {did_id:converted value, ...,did_id:converted value} and did id
                list lets take example you have passed more then one did in dictionary
                1) F18C 2)F186
                so, your did_dict parameter passing will be {0xF18C: 8, 0xF186: 1} and param convert_to="hex_list"
                return value will be {0xF18C:[0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20],0xF186:{0x01}},[0xF18C,0xF186]

        NOTE: You can pass multiple DID in only Read DID not in Write DID Method.!!!!
        """
        try:
            data_identifiers = {}
            did_list = []
            for key, value in did_dict.items():
                did_list.append(key)
                if convert_to == "ascii":
                    data_identifiers[key] = AsciiCodec(value)
                elif convert_to == "hex_list":
                    data_identifiers[key] = HexListCodec(value)
                elif convert_to == "int_list":
                    data_identifiers[key] = IntListCodec(value)
            return data_identifiers, did_list
        except ValueError as val_error:
            robot_print_error(f"Please Provide Valid Argument!, EXCEPTION:{val_error}")
        except Exception as exp:
            robot_print_error(f"Error to crate data identifiers, EXCEPTION:{exp}")

    def __create_io_identifiers(self, did_id: int, control_states: dict, control_masks: int = None) -> dict:
        """
        config['input_output']={0x300A:{"codec":MyCodec(4),
                        "mask":{'Byte':0xFDFFFFFF},'mask_size' : 4},0x3001:MyCodec(1)}
        :param control_masks: control masks
        :param control_states: control states
        :param did_id:diagnostic ID
        :return:
        """
        try:
            io_config = {}
            length = len(control_states)
            io_config[did_id] = {'codec': IOListCodec(length)}
            if control_masks is not None:
                io_config[did_id]['mask'] = {'Byte': control_masks, 'mask_size': length}
            return io_config
        except Exception as exp:
            robot_print_error(f"Error to crate io identifiers, EXCEPTION:{exp}")

    def change_session(self, session_id: int, is_suppress_bit: bool = False) -> dict:
        """
        This Function is used for change session

        Service Examples:
        Tx: 20 01 (Default Session) //Here 0x10 is service and 0x01 is session_id
        Rx: 50 01 //Here 0x50(0x10+0x40=0x50) = Positive Response and 0x01 is session_id

        :param: session_id :(str) Session values should be from [1,2,3] for respective session name given in list:
                ['Default','Programming','Extended']
        :param: is_suppress_bit(bool): If Suppress Bit set then ECU will assume server will give positive response so
                no response you will get(e.g;TX:10 80, RX: No Response) [Default is False]
        :return: (dict): updated dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response
        """
        try:
            with Client(self.connection, config=self.config) as client:
                if session_id in DEFAULT_OPTIONS:
                    if is_suppress_bit:
                        with client.suppress_positive_response:
                            resp = client.change_session(session_id)
                            robot_print_warning("Suppress Bit is Set so no Response from ECU")
                    else:
                        resp = client.change_session(session_id)
                    return self.__create_response(resp)
                else:
                    robot_print_error(f"Please Provide Valid Session ID")
                    raise Exception("Please Provide Valid Session ID")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def tester_present(self, is_suppress_bit: bool = False, is_extended_byte: bool = False,
                       extended_byte_len: int = None) -> dict:
        """
        This Function is used for Tester Present Activate to keep session active.
        Service Examples:
        Tx: 3E 00 00 //Here 0x3E is service 0x00 is sub function and 0x00 is Priority Byte
        Rx: 7E 00 //Here 0x7E(0x3E+0x40=0x7E) = Positive Response with Sub function

        :param: is_suppress_bit(bool): If Suppress Bit set then ECU will assume server will
                give positive response so no response you will get(e.g;TX:3E 80, RX: No Response)
                [Default is False]
        :param:is_extended_byte:(bool)If project requirement says more then 2 Bytes to send in Tester Present then this
                option should set to True
                [Default is False]
        :param:extended_byte_len:(bool)If user make is_extended_byte = True then Data Length Value of tester present
                need to pass here
                [Default is None]
        :return: (dict): update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response
        """
        try:
            with Client(self.connection, config=self.config) as client:
                extended_payload = b'\x3E'
                robot_print_info(f"Arguments as : {type(is_extended_byte), is_extended_byte}, {extended_byte_len}")
                if is_extended_byte and extended_byte_len is not None:
                    robot_print_info(
                        f"User set Tester present Request with extended Payload and length {extended_byte_len}", )
                    if is_suppress_bit:
                        extended_payload += b'\x80'
                        for i in range(2, int(extended_byte_len)):
                            extended_payload += b'\x00'
                        robot_print_info(f"Sending extended payload with values: {extended_payload}", )
                        with client.payload_override(extended_payload):
                            resp = client.tester_present()
                            robot_print_warning("Suppress Bit is Set so no Response from ECU")
                    else:
                        extended_payload += b'\x00'
                        for i in range(2, int(extended_byte_len)):
                            extended_payload += b'\x00'
                        robot_print_info(f"Sending extended payload with values: {extended_payload}")
                        with client.payload_override(extended_payload):
                            resp = client.tester_present()
                            robot_print_warning(
                                "Suppress Bit is Set as false but user provided is_extended_byte True", )
                else:
                    if is_suppress_bit:
                        with client.suppress_positive_response:
                            resp = client.tester_present()
                            robot_print_warning("Suppress Bit is Set so no Response from ECU")
                    else:
                        robot_print_info(
                            "Since is_extended_byte Flag not set TesterpresentRequest Payload Send is 2 Bytes :[3E 00]")
                        resp = client.tester_present()
            return self.__create_response(resp)
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def unlock_security_access(self, algo_dict: dict, depth: int = 1) -> dict:
        """
        This Function is used for Security Unlock

        :param: algo_dict(dict):All Security Levels Present in Project should be Provide here.
        Example Dict: Lets assume you have 3 security level in project and all has different algorithm to unlock
                     security accesses: 1) one's complement 2) two's complement 3)xor with mask all 0xF
        algo_dict = {
            0x01: {
                "algo": "ones_complement",  //Function name and Function should be Define by CRE team in CRE Folder
                "data": [0x12, 0x34, 0x56, 0x78, 0xF1, 0xF2, 0xF3, 0xF4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00]
                        //This data you can get from 27 01  67 01 [data] you can provide as give in above given format
                },
            0x03: {
                "algo": "twos_complement",  //Function name and Function should be Define by CRE team in CRE Folder
                "data": []
                        //This data you can get from 27 03  67 03 [data] you can provide as give in above given format
                },
            0x63: {
                "algo": "xor_algo",//Function name and Function should be Define by CRE team in CRE Folder
                "data": []
                    //This data you can get from 27 63  67 63 [data] you can provide as give in above given format
                }
                }
        :param: depth(int): user should mention how depth level security unlock they want
                [here Depth < 4 ][Default: 1]
        :return: (dict): update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response
        """
        try:
            for key, value in algo_dict.items():
                robot_print_info(f"{'-' * 20}SECURITY LEVEL {hex(key)} {'-' * 20}", True)
                if depth in SECURITY_LEVELS:
                    self.config['security_algo'] = value['algo']
                    self.config['security_algo_params'] = dict(key_list=value['data'])
                    with Client(self.connection, config=self.config) as client:
                        resp = client.unlock_security_access(int(key))
                        robot_print_debug(f"LEVEL {key} :{self.__create_response(resp)}", print_in_report=True)
                    return self.__create_response(resp)
                else:
                    robot_print_error(f"Security Levels should be from options:{SECURITY_LEVELS}")
                    raise Exception(f"Security Levels should be from options:{SECURITY_LEVELS}")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            self.is_trace = False
            return self.__create_response(None)

    def read_data_by_identifier(self, did_dict: dict, convert_to: str = "hex_list") -> dict:
        """
        This Function is used for read diagnostic identifier and return response as per covert to
            variable defined by user if not define then by default it return hex list
        :param did_dict: (dict) Here You should provide data as explained below
               only 1 DID Request:
               Syntax Example : did_id = {DID_ID: DID_DataLength_Code}
               Let's take example of Diagnostic Session Check DID 0xF186 which return 1 byte of data so your
               did_dict = {0xF186 : 1}
               Multiple DID Request:
               lets take example you have passed more then one did in dictionary
               1) F18C 2)F186
               so, your did_dict = {0xF18C: 8, 0xF186: 1}
        :param convert_to: (str) :value can be from list ["ascii","hex_list","int_list"]
               [Default value "hex_list"]
        :return: (dict): update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response (If Positive or Negative Response Code we get or any Exception you will receive
                response dictionary with proper code or empty and if Any NRC or Exception Error Message also
                print to notify)
        NOTE: If you ask to Read Multiple Did then please Group only those DID who's Covert to param match in .CDD File
        """
        try:
            robot_print_debug(f"Start reading by identifier with arguments: {did_dict}, convert_to: {convert_to}",
                              print_in_report=True)
            data_identifiers, did_list = self.__create_data_identifiers(did_dict, convert_to)
            self.config['data_identifiers'] = data_identifiers
            robot_print_debug("config['data_identifiers']:", self.config['data_identifiers'])
            with Client(self.connection, config=self.config) as client:
                resp = client.read_data_by_identifier(did_list)
                robot_print_debug(
                    f"{'-' * 20}{resp.service.get_name()} Got {resp.code_name}{'-' * 20}", print_in_report=True)
                return self.__create_response(resp)
        except ConfigError as config_error:
            robot_print_error(f"Please Provide valid 'convert_to' Parameter!! {config_error}")
            return self.__create_response(None)
        except (TypeError, AttributeError) as error:
            robot_print_error(f"Please Provide Valid Arguments:{error}")
            return self.__create_response(None)
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_warning(
                "Please Check if DID data Length if greater than 0, Provide your did_id in Dict Format")
            robot_print_error(f'Server sent an invalid payload: {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def write_data_by_identifier(self, did_dict: dict, data_to_write: list, convert_to: str = "hex_list") -> dict:
        """
        This Function is used for read diagnostic identifier and return response as per covert to
        variable defined by user if not define then by default it return hex list
        :param did_dict: (dict) This is Diagnostics ID list which you want to read
        :param data_to_write: (list): Give int or dict of did values to write into DID
        :param convert_to: (str) :value can be from list ["ascii","hex_list","int_list"]
               [Default = "hex_list"]
        :return: (dict): update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response(If Positive or Negative Response Code we get or any Exception you will receive
                response dictionary with proper code or empty and if Any NRC or Exception Error Message also
                print to notify)
        """
        try:
            if len(did_dict) == 1:
                # create Config
                data_identifiers, did_list = self.__create_data_identifiers(did_dict, convert_to)
                self.config['data_identifiers'] = data_identifiers
                robot_print_info("config['data_identifiers']:", self.config['data_identifiers'])
                # Step =3 : Write Diagnostic
                with Client(self.connection, config=self.config) as client:
                    resp = client.write_data_by_identifier(did_list[0], data_to_write)
                    robot_print_info(f"{'-' * 20}{resp.service.get_name()} Got {resp.code_name} {'-' * 20}")
                    return self.__create_response(resp)
            else:
                robot_print_error("Please Provide Only 1 DID Dict!!")
                raise Exception("Please Provide Only 1 DID Dict!!")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except ConfigError as config_error:
            robot_print_error(f"Please Provide valid 'convert_to' Parameter!!{config_error}")
            return self.__create_response(None)
        except TypeError as type_error:
            robot_print_error(f"Please Provide Valid Arguments:{type_error}")
            return self.__create_response(None)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_warning(
                "Please Check if DID data Length if greater than 0, Provide your did_id in Dict Format")
            robot_print_error(f'Server sent an invalid payload: {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def ecu_reset(self, reset_type: int, is_suppress_bit: bool = False) -> dict:
        """
        This Function is use to perform Reset ECU.
        :param reset_type: (int)  reset options are [1,2,3] and respective values are [HardReset, KeyOnReset, SoftReset]
        :param is_suppress_bit: (bool) If Suppress Bit set then ECU will assume server will give positive response so
               no response you will get(e.g;TX:10 80, RX: No Response)[Default is False]
        :return: (dict) update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response
        """
        try:
            if reset_type in DEFAULT_OPTIONS:
                with Client(self.connection, config=self.config) as client:
                    if is_suppress_bit:
                        with client.suppress_positive_response:
                            resp = client.ecu_reset(reset_type)
                            robot_print_warning("Suppress Bit is Set so no Response from ECU")
                    else:
                        resp = client.ecu_reset(reset_type)
                        robot_print_info(f"{'-' * 20}{resp.service.get_name()} Got {resp.code_name} {'-' * 20}")
                    return self.__create_response(resp)
            else:
                robot_print_error("Please Enter Valid Reset Type!!!")
                raise Exception("Please Enter Valid Reset Type!!!")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def clear_dtc(self, group: int = 0xFFFFFF) -> dict:
        """
        This Function is use to clear its active Diagnostic Trouble Codes
        :param: group:(int) The group of DTCs to clear. It may refer to Power train DTCs, Chassis DTCs, etc. Values are
               defined by the ECU manufacturer except for two specific values
                - ``0x000000`` : Emissions-related systems
                - ``0xFFFFFF`` : All DTCs
                [Default is 0xFFFFFFFF]
        :return: (dict) update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                response
        """
        try:
            if 0x000000 <= group <= 0xFFFFFF:
                with Client(self.connection, config=self.config) as client:
                    resp = client.clear_dtc(group)
                    robot_print_info(f"{'-' * 20}{resp.service.get_name()} Got {resp.code_name} {'-' * 20}")
                    return self.__create_response(resp)
            else:
                robot_print_error("Please Enter Valid DTC Group value!!!")
                raise Exception("Please Enter Valid DTC Group value!!!")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            self.is_trace = False
            return self.__create_response(None)

    def routine_control(self, routine_id: int, request_type: int = 1, data: int = None) -> dict:
        """
        This Function start routine
        :param routine_id: (int): Routine Diagnostic ID
        :param request_type: (int) : option should be from [1,2,3] respectively for ['start','stop','get_result']
               [Default is 1]
        :param data: (bytes) : Optional additional data to give [Default is None]
        :return: update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                 response
        """
        try:
            if request_type in DEFAULT_OPTIONS:
                with Client(self.connection, config=self.config) as client:
                    resp = client.start_routine(routine_id, request_type, data)
                    robot_print_info(f"{'-' * 20}{resp.service.get_name()} Got {resp.code_name} {'-' * 20}")
                    return self.__create_response(resp)
            else:
                robot_print_error("Please Enter Valid Routine Request Type!!!")
                raise Exception("Please Enter Valid Routine Request Type!!!")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def io_control(self, did_id: int, control_param: int, control_states: dict, control_masks: int = None) -> dict:
        """
        This Function input signal or overrides the state of an output by sending
        :param did_id:  Input Output Diagnostic ID
        :param control_param: (int) : This values Should be set from [0,1,2,3] respectively for ['Return Control To ECU'
               ,'Reset to default','Freeze Current State','Short-Term Adjustment']
                example: if user selected control_param =3 then frame will become 2F 30 01 03
        :param control_states: (dict) : A dict for named arguments as given below example
               Example:This 0x3001 DID has length of control state is 1 {'Byte0':0x01}
               Here Instead 'Byte0' or any customized name user can provide,
               and 0x01 is value set in Control_states so frame will become 2F 30 01 03 01
        :param control_masks: (int): User need to Provide mask value as per given in below example
               example: This 0x300A DID has length of control_states is 4 and has control_mask also present in .CDD file
                        mask use for enable disable bit
                        if we want to enable all you can pass 0xFFFFFFFF
                        if you want to disable all bits 0x00000000
                        if you want to set for example bit:2 of byte:0 to 0 and rest 1 then you need to
                        pass 0xFDFFFFFF(Byte0:1111 1101 (FD), Byte1:1111 1111 (FF),Byte2:1111 1111 (FF)),
                        Byte3:1111 1111 (FF)))
                        user need to provide
                        control_states={'Byte0': 0x01,'Byte1': 0x02,'Byte2': 0x03,'Byte3': 0x04}
                        control_masks = {'Byte':0xFFFFFFFF}
                        complete frame will be looks like 2F 30 01 03 01 02 03 04 FF FF FF FF
                [Default is None]
        :return: (dict) update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                 response
        """
        try:
            if control_param in IO_CONTROL_PARAM:
                self.config['input_output'] = self.__create_io_identifiers(did_id, control_states, control_masks)
                robot_print_debug(f"Config for IO Control: {self.config['input_output']}", print_in_report=True)
                with Client(self.connection, config=self.config) as client:
                    if control_masks is not None:
                        control_masks = ['Byte']
                    resp = client.io_control(did_id, control_param, control_states, control_masks)
                    return self.__create_response(resp)
            else:
                robot_print_error("Please Enter Valid Control Params in Argument!!!")
                raise Exception("Please Enter Valid Control Params in Argument!!!")
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)
        except (InvalidResponseException, UnexpectedResponseException) as e:
            robot_print_error(f'Server sent an invalid payload : {e.response.original_payload}')
            return self.__create_response(e.response)
        except TimeoutException as timeout_error:
            self.is_trace = False
            robot_print_error(f'Server not replied within given p2 time: {timeout_error}')
            return self.__create_response(None)

    def read_dtc_info(self, sub_function: int, status_mask: int):
        """
            This Function is used to read DTC information
            param sub_function: sub_function for the dtc information in integer
            param status_mask: status_mask in integer
            :return: (dict) update dictionary {"service_name": "","responseCode": 0,"codeName": "","data": []} as per
                 response


        """
        try:
            with Client(self.connection, config=self.config) as client:
                resp = client.read_dtc_information(subfunction=sub_function, status_mask=status_mask)
                robot_print_debug(f"response received from client>>>>>>>:{resp}")
                ReadDTCInformation.interpret_response(resp, subfunction=sub_function)
            return self.__create_response(resp)
        except NegativeResponseException as e:
            robot_print_error(f'Server refused our request for service {e.response.service.get_name()} with code '
                              f'"{e.response.code_name}" {e.response.code}')
            return self.__create_response(e.response)


class AsciiCodec(DidCodec):
    """
    This Class is for ASCII Conversion
    """

    def __init__(self, string_len):
        super().__init__()
        self.string_len = string_len

    def encode(self, string_ascii):
        """
        This Function calls Automatically  When We call Write DID
        :param string_ascii:Data you want to covert string ascii encoded value
        :return: encoded string ascii
        """
        return string_ascii.encode('ascii')

    def decode(self, string_bin):
        """
        This Function calls Automatically  When We call Read DID
        :param string_bin:Data you want to covert to ASCII String
        :return:ASCII String
        """
        return string_bin.decode('ascii')

    def __len__(self):
        return self.string_len


class HexListCodec(DidCodec):
    """
    This Class is for HexList Conversion
    """

    def __init__(self, string_len):
        super().__init__()
        self.string_len = string_len

    def encode(self, int_list) -> bytes:
        """
        This Function calls Automatically  When We call Write DID
        :param int_list:Data you want to covert hex  to bytes
        :return:byte list since data write in DID require byte type value
        """
        return bytes(int_list)

    def decode(self, list_data) -> list:  # working
        """
        This Function calls Automatically  When We call Read DID
        :param list_data:Data you want to covert to hex
        :return:hex_list
        """
        hex_list = []
        for i in range(len(list_data)):
            hex_list.append(hex(list_data[i]))
        return hex_list

    def __len__(self):
        return self.string_len


class IntListCodec(DidCodec):
    """
    This Class is for IntList Conversion
    """

    def __init__(self, string_len):
        super().__init__()
        self.string_len = string_len

    def encode(self, int_list):
        """
        This Function calls Automatically  When We call Write DID
        :param int_list:Data you want to covert int list  to bytes to write into DID
        :return:byte list since data write in DID require byte type value
        """
        byte_list = []
        for i in range(len(int_list)):
            byte_list.append(int(int_list[i], 16))
        return bytearray(byte_list)

    def decode(self, data_list):
        """
        This Function calls Automatically  When We call Read DID
        :param data_list:Data you want to covert to int list
        :return:int_list
        """
        int_list = []
        for i in range(len(data_list)):
            int_list.append(int(data_list[i]))
        return int_list

    def __len__(self):
        return self.string_len


class IOListCodec(DidCodec):
    """
    This Class is for Encode IO Control DID services.
    """

    def __init__(self, string_len):
        """
        This Constructor is used for take length in control_states in io_control service of UDS
        :param string_len: (int) length of control_states
        """
        super().__init__()
        self.string_len = string_len

    def encode(self, **kwargs):
        """
        This Function will get called automatically  when you use io_control 2F Service
        :param kwargs:(dict) Bytes of value in that key can be any customize string and value will be the
                    which user wants to set in that particular DID bytes
                    example:{''Byte0:0x01,'Byte1':0x02} which you will be pass by control states of io_control function
        :return: (bytearray): passed byte array to control input and output values
        """
        list_items = bytearray([])
        if self.string_len == len(kwargs):
            for key, value in kwargs.items():
                list_items.extend(struct.pack('B', value))
        else:
            robot_print_error("Please Provide {self.string_len} numbers of key value pair in control_state!!!",
                              print_in_report=True)
            raise Exception(f"Error to encode in class IOListCodec: Please Provide {self.string_len} numbers of key "
                            "value pair in control_state!!!")
        return list_items

    def __len__(self):
        return self.string_len
