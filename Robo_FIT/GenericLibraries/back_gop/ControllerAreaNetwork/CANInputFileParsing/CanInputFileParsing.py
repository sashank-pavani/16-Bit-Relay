import json
from typing import Union
import pandas as pd
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfigurationManager import ConfigurationManager, \
    robot_custom_print
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_info
import cantools
from cantools.database.can.database import Database
import os


class CanInputFileParsing:
    __CAN_SIGNAL_TYPE_TX = "TX"
    __CAN_SIGNAL_TYPE_RX = "RX"
    __CAN_SIGNAL_TYPE_MASTER = "MASTER"

    def __init__(self, channel_name):
        """
        This class is parse the input excel file and provide the according to user provided value in
        can_config_file.json.
        :param channel_name: The name of the channel to connect to.
        """
        try:
            self.config_manager = ConfigurationManager()
            self.input_file_path = self.config_manager.get_can_input_file_path()
            self.tx_input_sheet = pd.read_excel(self.input_file_path, sheet_name="TX")
            self.rx_input_sheet = pd.read_excel(self.input_file_path, sheet_name="RX")
            self.master_signal_input_sheet = pd.read_excel(self.input_file_path, sheet_name="MASTER")
            #robot_print_debug("XL sheet Read Objects Created!!")

            if channel_name == "single":
                can_db_file_path_ch1 = self.config_manager.get_can_db_file_path_ch("single")
                #robot_print_debug(can_db_file_path_ch1)
                self.database_single = CanDatabase.get_can_db_instance(can_db_file_path_ch1)
            if channel_name == "dual":
                can_db_file_path_ch1 = self.config_manager.get_can_db_file_path_ch("single")
                can_db_file_path_ch2 = self.config_manager.get_can_db_file_path_ch("dual")
                #robot_print_debug(can_db_file_path_ch1)
                #robot_print_debug(can_db_file_path_ch2)
                self.database_single = CanDatabase.get_can_db_instance(can_db_file_path_ch1)
                if can_db_file_path_ch2 is not None:
                    self.database_dual = CanDatabase.get_can_db_instance(can_db_file_path_ch2)
            #robot_print_debug("DBC Read Object Created!!")
        except IOError as io_error:
            robot_print_error(f"There is an exception to read the CAN input excel file or dbc file!!, "
                              f"Exception: {io_error}")
        except Exception as exp:
            robot_print_error(f"Error in CanInputFileParsing Class Constructor EXCEPTION:{exp}")

    def __get_sheet_object(self, signal_type: str) -> pd.DataFrame:
        """
        This Function return sheet object based on signal type user provide
        :param signal_type: Option "TX","RX", "MASTER"
        :return: Object of TX sheet or "MASTER" sheet as per signal_type param.
        """
        if signal_type == CanInputFileParsing.__CAN_SIGNAL_TYPE_TX:
            return self.tx_input_sheet
        elif signal_type == CanInputFileParsing.__CAN_SIGNAL_TYPE_MASTER:
            return self.master_signal_input_sheet
        elif signal_type == CanInputFileParsing.__CAN_SIGNAL_TYPE_RX:
            return self.rx_input_sheet

    def get_master_can_signal_des(self) -> list:
        """
        This Function return complete column values of "CAN_DES" list from XL sheet
        :return: complete column values of "CAN_DES" list
        """
        try:
            return self.master_signal_input_sheet['CAN_DES'].to_list()
        except Exception as exp:
            robot_print_error(f"Error to fetch the CAN signal from the can input excel file, EXCEPTION: {exp}")

    def get_can_message_name(self, can_des: str, database_num: int, signal_type: str = "TX") -> str:
        """
        This method is used to get the Arbitration ID from the given input Excel file
        :param signal_type: Type of the signal i.e. MASTER, TX,RX.
        :param can_des: CAN Description in Input Excel file.
        :param database_num: database number/channel number
        :return: -1 if no value present at Input Excel, Otherwise "Given value in Int"
        """
        try:
            sheet_obj = self.__get_sheet_object(signal_type=signal_type)
            user_given_can_message_name = sheet_obj[sheet_obj['CAN_DES'] == can_des]['CAN_MESSAGE_NAME']
            robot_print_info(user_given_can_message_name)
            if user_given_can_message_name.isnull().values.any():
                robot_print_error(f"Error in CAN_Input_Excel.xlsx CAN_MESSAGE_NAME is Nan "
                                  f"for {can_des} description...!!!")
                raise Exception(f"Error in CAN_Input_Excel.xlsx CAN_MESSAGE_NAME is Nan for "
                                f"{can_des} description...!!!")
            else:
                if self.__is_can_message_name_in_dbc(user_given_can_message_name.item(),
                                                     database_num=int(database_num)):
                    return user_given_can_message_name.item()
                else:
                    robot_print_error(f"Error in CAN_Input_Excel.xlsx for {can_des}  "
                                      f"CAN_MESSAGE_NAME ={user_given_can_message_name}Provided is"
                                      f" not Present in dbc file!!")
        except ValueError:
            robot_print_error(f"CAN_DES: {can_des} not found in CAN_Input_Excel.xlsx file!!")
        except Exception as exp:
            robot_print_error(f"Error to get can message name, Exception: {exp}")

    def __is_can_message_name_in_dbc(self, user_given_can_message_name: str, database_num: int) -> bool:
        """
        This Function returns True if the user provided can_message_name is found in the specified database, otherwise False.

        :param user_given_can_message_name: signal name
        :param database_num: Indicates which database to check (1 or 2).
        :return: True if can_message_name is found in the specified database, else False.
        """
        try:
            if database_num == 1:
                database = self.database_single
            elif database_num == 2:
                database = self.database_dual
            else:
                raise ValueError("Invalid database number. Use either 1 or 2.")

            for msg in database.messages:
                if msg.name == user_given_can_message_name:
                    robot_print_info(f"user_given_can_message_name:{user_given_can_message_name}")
                    return True
            return False
        except Exception as exp:
            robot_print_error(f"Error in __is_can_message_name_in_dbc EXCEPTION: {exp}")

    def get_msg_object_by_msg_name(self, message_name: str, database_num: int) -> cantools.db.Message:
        """
        This Function returns a message object by using message_name from the specified database.

        :param message_name: Message name which is in dbc.
        :param database_num: Indicates which database to use (1 or 2).
        :return: Message object.
        """

        if int(database_num) == 1:
            database = self.database_single
        elif int(database_num) == 2:
            database = self.database_dual
        else:
            raise ValueError("Invalid database number. Use either 1 or 2.")
        value = self.__is_can_message_name_in_dbc(message_name, database_num)
        if value:
            return database.get_message_by_name(message_name)

    def get_msg_object_by_can_des(self, can_des: str, database_num: int,
                                  signal_type: str = "TX") -> cantools.db.Message:
        """
        This Function return msg object by using message_name
        :param signal_type: Type of the signal i.e. MASTER, TX,RX.
        :param can_des: CAN Description in Input Excel file.
        :param database_num: Indicates which database to use (1 or 2).
        :return:
        """
        msg_name = self.get_can_message_name(can_des, database_num=database_num, signal_type=signal_type)

        if database_num == 1:
            return self.database_single.get_message_by_name(msg_name)
        elif database_num == 2:
            return self.database_dual.get_message_by_name(msg_name)
        else:
            raise ValueError("Invalid database number. Use either 1 or 2.")

    def display_signal_values(self, can_des, database_num: int, signal_type: str = "TX"):
        """
        This Function displays Signal Tree and choices for the specified database channel.

        :param signal_type: Type of the signal i.e. TX, "RX", "MASTER".
        :param can_des: CAN Description in the input Excel file.
        :param database_num: Indicates which database to use (1 or 2).
        :return: None
        """
        if database_num == 1:
            database = self.database_single
        elif database_num == 2:
            database = self.database_dual
        else:
            raise ValueError("Invalid database number. Use either 1 or 2.")

        can_msg_name = self.get_can_message_name(can_des, database_num=int(database_num), signal_type=signal_type)
        can_message_signals = database.get_message_by_name(can_msg_name).signals
        info_str = ""
        info_str += f"{'-' * 30}{can_msg_name}{'-' * 30}\n"
        info_str += f"  Signal tree:\n    -- {{root}} {can_msg_name}\n"

        for index in range(len(can_message_signals)):
            info_str += f"       +-- {can_message_signals[index].name}\n"

        info_str += "  Signal choices:\n"

        for can_message_signal in can_message_signals:
            info_str += f"    {can_message_signal.name}\n"
            if can_message_signal.choices is not None:
                for key, value in can_message_signal.choices.items():
                    info_str += f"        {key} {value}\n"
            else:
                info_str += f"        {can_message_signal.choices}"

        robot_custom_print(text=info_str, color='blue')

    def get_available_choices(self, msg: cantools.db.Message) -> dict:
        """
        This Function return Message.Signals.choices in dict format
        :param msg: message object
        :return: available_choices_dict
        """
        try:
            available_choices_dict = {}
            for signal in msg.signals:
                signal_name = signal.name
                signal_choices = signal.choices
                if signal_choices is not None:
                    available_choices_dict[signal_name] = dict(signal_choices)
                else:
                    available_choices_dict[signal_name] = None
                    min = signal.minimum
                    max = signal.maximum
                    if min == max:
                        available_choices_dict[signal_name] = [0]
                    else:
                        available_choices_dict[signal_name] = (min, max)
            return available_choices_dict
        except Exception as exp:
            robot_print_error(f"Error to get_available_choices , EXCCEPTION:{exp}")

    def __is_json_signal_choices_are_valid(self, msg: cantools.db.Message, json_data: dict, can_des: str,
                                           database_num: int,
                                           signal_type: str = "TX") -> bool:
        """
        This Function check if Signal Choices in JSON Format frame correct or not!!
        :param msg: message object
        :param json_data: json data passed by user in ~$CAN_Input_Excel.xlsx
        """
        available_choices_dict = {}
        try:
            available_choices_dict = self.get_available_choices(msg)
            # check json_data
            for key, value in json_data.items():
                available_choices = available_choices_dict[key]
                if isinstance(available_choices, dict):
                    if value not in available_choices:
                        self.display_signal_values(can_des=can_des, database_num=int(database_num),
                                                   signal_type=signal_type)
                        robot_print_info(f"{'-' * 10}Please correct Signal Choices in json value and Try Again!!"
                                         f"{'-' * 10}\nInvalid Choice value for {key}:{value}\n"
                                         f"available choices are:{available_choices_dict[key]}\n"
                                         f"Signal Tree and Choices given above for more detail\n{'-' * 80}")
                        return False
                elif isinstance(available_choices, tuple):
                    if int == type(available_choices[1]):
                        int(value)
                    else:
                        float(value)
                    if available_choices[0] <= value <= available_choices[1]:
                        return True
                    else:
                        self.display_signal_values(can_des=can_des, database_num=int(database_num),
                                                   signal_type=signal_type)
                        robot_print_info(f"{'-' * 10}Please correct Signal Choices in json value and Try Again!!"
                                         f"{'-' * 10}\nInvalid Choice value for {key}:{value}\n"
                                         f"available choices are:{available_choices_dict[key]}\n"
                                         f"Signal Tree and Choices given above for more detail\n{'-' * 80}")
            return True
        except KeyError as exp:
            robot_print_debug(f"KeyError:{exp}\nAvailable Keys are:{available_choices_dict.keys()}")
        except Exception as exp:
            robot_print_error(f"Error in is_signal_choices_are_valid EXCEPTION:{exp}")

    #
    def __convert_json_data_to_bytearray(self, can_des: str, database_num: int, json_data: dict,
                                         signal_type: str = "TX") -> bytearray:
        """
        This Function Fill rest of message signal which is no need to modify to 0 and make complete json if complete
        json not given else user given json will be used and convert to bytearray.
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        :param json_data: json data user gave
        :return: json to bytearray converted data
        """
        try:
            robot_print_info(f"USER DATA:{json_data}")
            msg = self.get_msg_object_by_can_des(can_des, database_num=database_num, signal_type=signal_type)
            message_length = msg.length
            if message_length != len(json_data):
                user_signal_list = list(dict(json_data).keys())
                # print(user_signal_list)
                # check if user signal name list is subset of original signal name list of DBC!!
                if set(user_signal_list).issubset(set(msg.signal_tree)):
                    # if signal assigned values also correct
                    if self.__is_json_signal_choices_are_valid(msg, json_data, can_des, database_num=database_num,
                                                               signal_type=signal_type):
                        # Not Provided signal and it's value append & assign with 0 and create CAN frame in bytearray
                        print("JSON_CHOICE is VALID")
                        for signal in msg.signal_tree:
                            if signal not in user_signal_list:
                                json_data[signal] = 0
                        #robot_print_debug(f"COMPLETE JSON DATA TO SEND:{json_data}")
                        return msg.encode(json_data)
                    else:
                        raise Exception("\nInvalid Choice for signal value, For more Detail Check Above "
                                        "INFO statement")
                else:  # signal name given is not present in DBC will raise exception guide!!!
                    robot_print_debug(f"\n{'-' * 10}Please correct Signal Name in json value and Try Again!!"
                                      f"{'-' * 10}\n\nError in CAN_Input_Excel.xlsx in Sheet_Name:{signal_type} "
                                      f"CAN DES:{can_des} \n\nInvalid Signal Value Given which is not in DBC file :"
                                      f"{set(user_signal_list) - set(msg.signal_tree)}\n"
                                      f"USER Signal list:{user_signal_list}\n"
                                      f"Your Signal name should from:{msg.signal_tree}\n{'-' * 80}")
                    # self.display_signal_values( can_des, signal_type )
                    raise Exception(f"\nInvalid Signal Value Given which is not in DBC file :"
                                    f"{set(user_signal_list) - set(msg.signal_tree)} For More Detail check above "
                                    f"INFO statement")
        except Exception as exp:
            robot_print_error(f"Error to __convert_json_data_to_bytearray EXCEPTION:{exp}")

    def __is_can_frame_signal_choices_valid(self, msg: cantools.db.Message, database_num, json_data: dict,
                                            can_des: str,
                                            signal_type: str = "TX") -> bool:
        """
        This Function check if Signal Choices in JSON Format frame correct or not!!
        :param msg: message object
        :param json_data: json data passed by user in ~$CAN_Input_Excel.xlsx
        """
        available_choices_dict = {}
        try:
            available_choices_dict = self.get_available_choices(msg)
            # check json_data
            for key, value in json_data.items():
                available_choices = available_choices_dict[key]
                if isinstance(available_choices, dict):
                    if value not in available_choices.values():
                        self.display_signal_values(can_des=can_des, database_num=database_num,
                                                   signal_type=signal_type)
                        robot_print_info(f"{'-' * 10}Please correct Signal Choices in json value and Try Again!!"
                                         f"{'-' * 10}\nInvalid Choice value for {key}:{value}\n"
                                         f"available choices are given below in (type='decimal':value) format:\n"
                                         f"{available_choices_dict[key]}\n"
                                         f"Signal Tree and Choices given above for more detail\n{'-' * 80}")
                        return False
                elif isinstance(available_choices, tuple):
                    if available_choices[0] <= value <= available_choices[1]:
                        return True
                    else:
                        self.display_signal_values(can_des=can_des, database_num=database_num,
                                                   signal_type=signal_type)
                        robot_print_info(f"{'-' * 10}Please correct Signal Choices in json value and Try Again!!"
                                         f"{'-' * 10}\nInvalid Choice value for {key}:{value}\n"
                                         f"available choices are given below in (type='decimal':value) format:\n"
                                         f"{available_choices_dict[key]}\n"
                                         f"Signal Tree and Choices given above for more detail\n{'-' * 80}")
            return True
        except KeyError as exp:
            robot_print_debug(f"KeyError:{exp}\nAvailable Keys are:{available_choices_dict.keys()}")
        except Exception as exp:
            robot_print_error(f"Error in is_signal_choices_are_valid EXCEPTION:{exp}")

    def __convert_can_frame_to_bytearray(self, can_data: pd.Series, can_des: str, database_num: int,
                                         signal_type: str = "TX") -> bytearray:
        """
        This Function Convert 60,0,0,0,0,0,0,0 to bytearray(b'<\x00\x00\x00\x00\x00\x00\x00')
        :param can_data: can data user given in CAN_Input_Excel.xlsx column CAN_DATA
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        :return: can_frame to bytearray
        """
        msg = self.get_msg_object_by_can_des(can_des, database_num, signal_type)
        try:
            # can_data = can_data.values.any()
            can_data= can_data.values[0].strip()
            robot_print_info(f"can_data :{can_data}")
            # if isinstance(can_data, str) and "," in can_data:
            if len(can_data) > 2:
                can_data = [int(i.strip(), base=16) for i in can_data.split(",")]
            # if isinstance(can_data, str) and "," in can_data:
            #     can_data_list = [self.convert_hex_to_signed_int(i.strip()) for i in can_data.split(",")]
            else:
                can_data = [int(can_data[0])]
            if len(can_data) == msg.length:
                robot_print_info(f"It seems you provide CAN frame in CAN input excel!!!")
                json_data = msg.decode(bytearray(can_data))
                #robot_print_debug(f"CAN_FRAME_TO_JSON DATA:{json_data}")
                if self.__is_can_frame_signal_choices_valid(msg, database_num, json_data, can_des, signal_type):
                    return bytearray(can_data)
                else:
                    raise Exception(
                        f"\nError in CAN_Input_Excel.xlsx in Sheet_Name:{signal_type} CAN DES:{can_des} "
                        "For more detail check statement")
            else:
                raise Exception(f"\nError in CAN_Input_Excel.xlsx in Sheet_Name:{signal_type} CAN DES:{can_des} "
                                f"CAN Frame Length should be :{len(msg.signal_tree)} and Given CAN Frame length is "
                                f"{len(can_data)}")
        except ValueError:
            info_str = f"\n{'-' * 30}{msg.name} Message Available Choices:{'-' * 30}"
            for key, value in self.get_available_choices(msg=msg).items():
                info_str += f"\n{key}:{value}"
            robot_print_info(text=info_str)
            robot_print_error(f"\nError in CAN_Input_Excel.xlsx in Sheet_Name:{signal_type} CAN DES:{can_des} "
                              f"\nInvalid CAN Data :{can_data}\n for more detail check info given in above statement")
        except Exception as exp:
            robot_print_error(f"Error to __convert_can_frame_to_bytearray :EXCEPTION:{exp}")

    def convert_hex_to_signed_int(self, hex_str):
        """
        Convert a hexadecimal string to a signed integer.
        :param hex_str: Hexadecimal string
        :return: Signed integer
        """
        value = int(hex_str, 16)
        # Determine if the value should be negative based on its length
        if value >= (1 << 7):  # 8-bit value (1 << 7) == 128
            value -= (1 << 8)  # 8-bit value (1 << 8) == 256
        return value
    def get_can_data(self, can_des, database_num: int, signal_type: str = "TX") -> Union[bytearray, None]:
        """
        This method is used to get the CAN Data from the given input Excel file
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        :param database_num: database_num /channel number
        :return: {}(empty dict) if no value present at Input Excel, Otherwise "Given value in Dict"
        """
        try:
            if self.get_can_message_name(can_des=can_des, database_num=database_num, signal_type=signal_type):
                sheet_obj = self.__get_sheet_object(signal_type)
                can_data = sheet_obj[sheet_obj['CAN_DES'] == can_des]['CAN_DATA']
                if can_data.isnull().values.any():
                    robot_print_error(f"The CAN Data is Nan for {can_des} description...!!!")
                    raise Exception(f"The CAN Data is Nan for {can_des} description...!!!")
                else:
                    try:
                        # handle internally
                        json_data = json.loads(list(can_data.to_dict().values())[0])
                        return self.__convert_json_data_to_bytearray(can_des=can_des, json_data=json_data,
                                                                     database_num=database_num,
                                                                     signal_type=signal_type)
                    except json.JSONDecodeError:
                        return self.__convert_can_frame_to_bytearray(can_data, can_des, database_num, signal_type)
            else:
                return None
        except IndexError:
            robot_print_error(f"CAN_DES: {can_des} not found in CAN_Input_Excel.xlsx file!!")
        except Exception as exp:
            robot_print_error(f"There is an error to get_can_data, Exception:{exp}")

    def get_decoded_data(self, message_name: str, database_num, user_data: bytearray) -> json:
        """
        This Function bytearray to json data Decode Data
        :param message_name: message name
        :param user_data: user data
        :param database_num: database_num /channel number
        :return: json data
        """
        msg = self.get_msg_object_by_msg_name(message_name, database_num)
        return msg.decode(user_data)

    def get_max_step_count(self, message_name, database_num) -> int:
        """
        This Function return max step count of message
        :param message_name: message name
        :param database_num: database_num /channel number
        :return: max step count
        """
        msg = self.get_msg_object_by_msg_name(message_name, database_num)
        available_choices_dict = self.get_available_choices(msg)
        for signal in msg.signals:
            if signal.name.upper().endswith("COUNT") or signal.name.upper().endswith(
                    "CNT") or "COUNT" in signal.name.upper():
                signal_name = signal.name
                return available_choices_dict[signal_name][1]
        else:
            raise ValueError("Message Step Count Signal Not Found!!!")

    def get_msg_step_count(self, message_name: str, database_num, user_data: bytearray) -> Union[int, None]:
        """
        This Function is returning message count
        :param message_name: message name
        :param database_num: database number /channel number
        :param user_data: user data
        :return: if CRC value found then return message step count else None
        """
        try:
            json_data = self.get_decoded_data(message_name, database_num, user_data)
            print(json_data)
            for key in json_data.keys():
                if key.upper().endswith("COUNT") or key.upper().endswith("CNT") or "COUNT" in key.upper():
                    #robot_print_debug(f"Message: {message_name} contains CRC as {key}", print_in_report=True)
                    #robot_print_debug(f"Roll Count of {message_name} is {json_data[key]}")
                    return json_data[key]
            #robot_print_debug(f"Message: {message_name} not contain CRC value", print_in_report=True)
            return None
        except Exception as exp:
            robot_print_error(
                f"Error to check the Message Step Count value of the {message_name}, EXCEPTION: {exp}")
            return None

    def get_can_signal_timeout(self, can_des, signal_type: str = "TX") -> float:
        """
        This method is used to get the CAN signal timeout from the given input Excel file
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        :return: -1 if no value present at Input Excel, Otherwise "Given value in Float"
        """
        try:
            sheet_obj = self.__get_sheet_object(signal_type)
            can_signal_timeout = sheet_obj[sheet_obj['CAN_DES'] == can_des]['TIMEOUT']
            if can_signal_timeout.isnull().values.any():
                robot_print_error(f"The CAN Signal timeout is Nan for {can_des} description...!!!")
                return -1
            else:
                return float(can_signal_timeout.values)
        except TypeError:
            robot_print_error(f"CAN_DES: {can_des} not found in CAN_Input_Excel.xlsx file!!")
        except Exception as exp:
            robot_print_error(f"There is an error to read an CAN input excel file, Exception:  {exp}")


class CanDatabase:
    """
    This class is used to manage multiple Database instances for CAN.
    """
    _instances = {}

    @staticmethod
    def get_can_db_instance(db_file_path) -> cantools.database.Database:
        """
        This method provides a CAN database instance. If an instance with the given file path exists, it returns that instance.
        Otherwise, it creates a new instance and stores it in the dictionary.

        :param db_file_path: Path of the Database file used to read the CAN signals.
        :return: CAN database instance.
        """
        if db_file_path not in CanDatabase._instances:
            db_path = os.path.join(db_file_path)
            #robot_print_info(f"db_path:{db_path}")
            CanDatabase._instances[db_file_path] = CanDatabase(db_file_path=db_path).can_db
        return CanDatabase._instances[db_file_path]

    def __init__(self, db_file_path):
        if db_file_path not in CanDatabase._instances:
            try:
                print(db_file_path)
                self.can_db = cantools.database.load_file(db_file_path)
                CanDatabase._instances[db_file_path] = self
            except cantools.Error as can_tools_error:
                print("There is an error while reading the CAN Database files:\nException %s" % can_tools_error)
        else:
            self.can_db = CanDatabase._instances[db_file_path].can_db
