import re
import sys
from typing import Union, Tuple
import cantools
from openpyxl import load_workbook
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.ConfigurationManager import ConfigurationManager, \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_custom_print


class MakeCanInputData:
    """
    This Class make CAN Input Data based on Message Name user Provide and Message Signal Values
    Result Data: Json Frame and CAN Frame to keep in CAN_Input_Excel.xlsx
    Purpose: To Avoid Opening DBC and Mapping data using this Class data to keep in CAN_Input_Excel.xlsx will get
    ready!!
    """
    CLOSE_TERMNAL_VALUE_LIST = ["quit", "q", "exit"]

    def __init__(self, root_path, team_name):
        try:
            self.helper = CommonKeywordsClass()
            self.helper.set_root_directory(root_path)
            if not self.helper.check_team_name(str(team_name).upper()):
                sys.exit("Invalidate Team name argument pass, Stopping Execution."
                         "\nPlease check the argument and run again")
            robot_print_debug(text=f"Team Name: {self.helper.team_name}", print_in_report=True, underline=True)
            self.config_manager = ConfigurationManager()
            self.db_file_path_single = self.config_manager.get_can_db_file_path_ch("single")
            robot_print_debug(f"database path for single channel---{self.db_file_path_single}")
            self.can_input_file = self.config_manager.get_can_input_file_path()
            self.database_single = cantools.db.load_file(self.db_file_path_single)
            robot_print_debug(f"database path for second channel---{self.database_single}")
            self.db_file_path_dual = self.config_manager.get_can_db_file_path_ch("dual")
            if self.db_file_path_dual is not None:
                self.database_dual = cantools.db.load_file(self.db_file_path_dual)
            self.is_running = True
            self.__is_print_tree = True
            self.book = None
        except FileNotFoundError as exp:
            robot_print_error(f"Exception :{exp}")
            sys.exit(exp)
        except OSError as exp:
            robot_print_error(f"Exception :{exp}")
            sys.exit(exp)

    def __print_message_name_list(self):
        """
        Printing Message name and Signal tree value for User Reference to avoid DBC opening!!
        """
        data_num = int(input("\nPlease specify the Database Channel number u want to add the can data:"))
        print(f"\n{'-' * 40}Make CAN Input Data:{'-' * 40}\n")
        if data_num == 1:
            for msg in self.database_single.messages:
                if not msg.is_multiplexed():
                    print("--", msg.name)
                    print("     Signal Tree:")
                    for signal_name in msg.signal_tree:
                        print(f"        +--{signal_name}")
            return data_num
        elif data_num == 2:
            for msg in self.database_dual.messages:
                if not msg.is_multiplexed():
                    print("--", msg.name)
                    print("     Signal Tree:")
                    for signal_name in msg.signal_tree:
                        print(f"        +--{signal_name}")
            return data_num

    def __get_message_name(self) -> Tuple[bool, Union[cantools.db.Message, None]]:
        """
        This Function get message name user provide it will print message name suggestion also if similar name
        value present in DBC if no possibility of user message name in DBC print message "Message Not Found!!"
        :return: bool,message name
        """
        data_num = ''
        if self.__is_print_tree:
            data_num = self.__print_message_name_list()
        user_msg_name = input("\n(Enter Case Sensitive Full  Message Name from Above Given list) 'OR' "
                              "(Enter Message/Signal name you remember it will give you suggestion): ")
        if user_msg_name.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
            raise KeyboardInterrupt
        if data_num == 1:
            for msg in self.database_single.messages:
                if user_msg_name == msg.name:
                    return True, msg
            for message in self.database_single.messages:
                if re.search(user_msg_name, message.name):
                    print(f"Do you mean :{message.name}")
                else:
                    if not message.is_multiplexed():
                        for signal in message.signal_tree:
                            if re.search(user_msg_name, signal):
                                print(f"Do you mean Message Name: {message.name}\t[{signal} is Signal Name in Message "
                                      f"{message.name}]")

        if data_num == 2:
            for msg in self.database_dual.messages:
                if user_msg_name == msg.name:
                    return True, msg
            for message in self.database_dual.messages:
                if re.search(user_msg_name, message.name):
                    print(f"Do you mean :{message.name}")
                else:
                    if not message.is_multiplexed():
                        for signal in message.signal_tree:
                            if re.search(user_msg_name, signal):
                                print(f"Do you mean Message Name: {message.name}\t[{signal} is Signal Name in Message "
                                      f"{message.name}]")
        return False, None

    def __get_signal_choices(self, signal: cantools.db.Message.signals) -> Union[int, float]:
        """
        This Function get signal choices user provide !!
        :param signal: signal object
        :return: choice value
        """
        user_signal_choice = "INVALID"
        if signal.choices is not None:
            print(f"\nSignal {signal.name} Choices Given in Below list:")
            for choice, description in signal.choices.items():
                print(f"{choice}:{description}")
            try:
                user_signal_choice = input(f"Select Signal '{signal.name}' value from:"
                                           f"{list(signal.choices.keys())}:")
                if user_signal_choice.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
                else:
                    user_signal_choice = int(user_signal_choice)
            except TypeError as exp:
                robot_print_error(f"user_signal_choice:{user_signal_choice} can't convert to int please provide valid"
                                  f" value!!!\nEXCEPTION:{exp}")
            if user_signal_choice in signal.choices.keys():
                return int(user_signal_choice)
            else:
                raise ValueError(f"user_signal_choice={user_signal_choice} not in {list(signal.choices.keys())}")
        else:
            if signal.minimum != signal.maximum:
                try:
                    user_signal_choice = input(f"Select Signal '{signal.name}' Value from Given Range :"
                                               f"{(signal.minimum, signal.maximum)} and it's unit({signal.unit}):")
                    if user_signal_choice.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                        raise KeyboardInterrupt
                    else:
                        user_signal_choice = int(user_signal_choice)
                except TypeError as exp:
                    robot_print_error(f"user_signal_choice:{user_signal_choice} can't convert to  please provide "
                                      f"valid value!!!\nEXCEPTION:{exp}")
                if type(signal.maximum) == int:
                    user_signal_choice = int(user_signal_choice)
                else:
                    user_signal_choice = float(user_signal_choice)
                if signal.minimum <= user_signal_choice <= signal.maximum:
                    return user_signal_choice
                else:
                    raise ValueError(f"user_signal_choice={user_signal_choice} not in Range:"
                                     f"{(signal.minimum, signal.maximum)}")
            else:
                print(f"\nSignal {signal.name} Choice =0")
                return 0

    def __create_json_data(self, message: cantools.db.Message) -> Union[dict, None]:
        """
        This Function return json_data
        :param message:message object
        :return: json_data
        """
        json_data = {}
        for signal in message.signals:
            try:
                choice = self.__get_signal_choices(signal)
                json_data[signal.name] = choice
            except ValueError:
                return None
        return json_data

    def __format_json_data(self, json_data) -> str:
        """
        This Function return formatted JSON String Data
        :param json_data: json dict data
        :return: string json data
        """
        format_json = '{\n'
        for key, value in json_data.items():
            format_json += f'"{key}":{value},\n'
        format_json = format_json[:-2]
        format_json += '\n}'
        return format_json

    def __append_data_to_input_xl(self, can_des, msg_name, data: str):
        """
        If user want to add data in XL sheet
        :param can_des: can description name user given
        :param msg_name: message name
        :param data: json_data write in XL
        """
        input_xl_path = ""
        try:
            sheet_name = input("Please Provide Sheet Name from:['TX','RX','MASTER']:")
            if sheet_name.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                raise KeyboardInterrupt
            while type(sheet_name) == str and sheet_name.upper() not in ['TX', 'RX', 'MASTER']:
                robot_custom_print("Please Provide Valid sheet Name value !!", color="yellow")
                sheet_name = input("Please Provide Sheet Name from:['TX','RX','MASTER']:")
                if sheet_name.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
            input_xl_path = self.config_manager.get_can_input_file_path()
            self.book = load_workbook(input_xl_path)
            sheet = self.book.get_sheet_by_name(sheet_name.upper())
            sheet.append([can_des, msg_name, data])
            self.book.save(input_xl_path)
            print(f"{'-' * 10}Data Saved to CAN_Input_Excel.xlsx{'-' * 10}")
            self.book.close()
        except FileNotFoundError:
            robot_print_error(f"File CAN_Input_Excel.xlsx not Present in Path: {input_xl_path}")
        except Exception as exp:
            robot_print_error(f"Error to add_data_to_input_xl: {exp}")

    def __add_data_to_xl(self, message: cantools.db.Message, formatted_json, hex_list):
        """
        This Function add data to xl based on user decide which format data they want keep and do thwy want to save
        or not in xl file!!
        :param message: message object
        :param formatted_json: json
        :param hex_list: can frame
        :return: None
        """
        try:
            yes_or_no = input("\nDo you want to add data to XL ?[y/n]:")
            if yes_or_no.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                raise KeyboardInterrupt
            while type(yes_or_no) == str and yes_or_no.lower() not in ['y', 'n']:
                robot_custom_print("Please Provide Correct value!!", color="yellow")
                yes_or_no = input("Do you want to add data to XL ?[y/n]:")
                if yes_or_no.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
            if yes_or_no.lower() == 'y':
                format_choice = input("Which Kind of data you want to add to XL ??(1:json, 2:can_frame):")
                if format_choice.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
                while type(format_choice) == str and format_choice.lower() not in ['1', '2']:
                    robot_custom_print("Please Provide format_choice value!!", color="yellow")
                    format_choice = input("Which Kind of data you want to add to XL ??(1:json, 2:can_frame):")
                    if format_choice.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                        raise KeyboardInterrupt
                can_des = input("Provide CAN_DES value for Signal:")
                if can_des.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
                if format_choice in ['1', '2']:
                    if format_choice == '1':
                        data = formatted_json
                    else:
                        data = hex_list
                    self.__append_data_to_input_xl(can_des.upper(), message.name, data)
                else:
                    robot_custom_print("Please Provide valid format choice!!", color="yellow")
        except Exception as exp:
            robot_print_error(f"Error to get yes_or_no for xl data write or not EXCEPTION:{exp}")

    def make_can_input_data(self):
        """
        This Function use to perform operation given define in above given methods
        """
        try:
            while self.is_running:
                option = input("\nDo you need DBC Signal Tree Print Again??[y/n]:")
                if option.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
                while type(option) == str and option.lower() not in ['y', 'n']:
                    robot_custom_print("Please Provide Correct value!!", color="yellow")
                    option = input("Do you need DBC Signal Tree Print Again??[y/n]:")
                    if option.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                        raise KeyboardInterrupt
                if option == 'n':
                    self.__is_print_tree = False
                status, message = self.__get_message_name()
                while status == False and message is None:
                    robot_custom_print("Please Provide Correct Message Name!!", color="yellow")
                    self.__is_print_tree = False
                    status, message = self.__get_message_name()
                json_data = self.__create_json_data(message)
                while json_data is None:
                    robot_custom_print("Please Provide Valid Signal Choice!!!(See Above Given Options)", color="yellow")
                    json_data = self.__create_json_data(message)
                formatted_json = self.__format_json_data(json_data)
                print(f"{'=' * 30}\n          Final JSON Data\n{'=' * 30}\n{formatted_json}")
                hex_list = ",".join([hex(x)[2:] for x in list(message.encode(json_data))])
                print(f"{'=' * 30}\n          Final CAN FRAME\n{'=' * 30}\nCAN_FRAME: {hex_list} ")
                self.__add_data_to_xl(message, formatted_json, hex_list)
                y_or_n = input("\nDo you want to Continue ??[y/n]:")
                if y_or_n.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                    raise KeyboardInterrupt
                while type(y_or_n) == str and y_or_n.lower() not in ['y', 'n']:
                    robot_custom_print("Please Provide Correct value!!", color="yellow")
                    y_or_n = input("Do you want to Continue ??[y/n]:")
                    if y_or_n.lower() in MakeCanInputData.CLOSE_TERMNAL_VALUE_LIST:
                        raise KeyboardInterrupt
                if y_or_n.lower() == 'n':
                    self.is_running = False
        except KeyboardInterrupt:
            if self.book is not None:
                robot_custom_print("Wait until everything will get closed!!", color="yellow")
                self.book.close()
                robot_custom_print(f"{'-' * 10}Done with Closing{'-' * 10}", color="green")
                sys.exit()

    def __del__(self):
        if self.book is not None:
            self.book.close()


if __name__ == '__main__':
    arguments = sys.argv
    data = MakeCanInputData(arguments[1], arguments[2])
    data.make_can_input_data()
