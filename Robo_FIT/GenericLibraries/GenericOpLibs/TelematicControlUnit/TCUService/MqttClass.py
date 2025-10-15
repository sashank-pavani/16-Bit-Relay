from Robo_FIT.GenericLibraries.GenericOpLibs.TelematicControlUnit.ExcelInputParsing.ParseInputExcel import \
    ParseInputExcel
from Robo_FIT.GenericLibraries.GenericOpLibs.TelematicControlUnit.TCUService.ValidateResponse import ValidateResponse
from Robo_FIT.GenericLibraries.GenericOpLibs.TelematicControlUnit.TCUService.MqttConnect import MqttConnect
from Robo_FIT.GenericLibraries.GenericOpLibs.TelematicControlUnit.TCUService.ConfigurationManager import \
    ConfigurationManager
import os
import json
import time
import queue
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass

display = True


class MqttClass(MqttConnect):
    _MSG_TYPE_CONNACK = "CONNACK"
    _MSG_TYPE_DISCONNECT = "DISCONNECT"
    _MSG_TYPE_SUBACK = "SUBACK"
    _MSG_TYPE_PUBACK = "PUBACK"
    _MSG_TYPE_CHKSUBS = "CHECKSUBS"
    _MSG_TYPE_UNSUBCAK = "UNSUBACK"
    _loopflag = True

    # user published messages dict
    _message_dict = {}
    _comparision_result = []
    _broker_response = ""
    _BROKER_MESSAGES = queue.Queue()

    def __init__(self):
        """
        This class provide the interface to connect, subscribe topic, publish message, validate broker response.
        """
        self.common_keywords = CommonKeywordsClass()
        self.config_manager = ConfigurationManager()
        super().__init__(self.config_manager.get_broker_address())
        # get the client instance for publishing and subscribing
        self.client = object
        # TODO : Need To check
        self.excel_file_path = os.path.join(self.common_keywords.get_root_path(),
                                            self.config_manager.get_input_excel_path())

    def __set_user_login(self):
        if self.config_manager.get_user_id() != "" and self.config_manager.get_user_password() != "":
            self.set_user_login(self.config_manager.get_user_id(), self.config_manager.get_user_password())

    def create_client_instance(self, client_id: str):
        """
        Provide the instance of client, By calling this method multiple times to create a Multi Client.
        :param client_id: Unique Id of client
        """
        self.__set_user_login()
        self.client = self.connect_to_server(client_id=client_id)
        print(f"Client Object: {self.client}")

    def __convert(self, msg) -> str:
        """
        This is a helper function to replace all chars outside BMP with a !
        :param msg: message comes from broker
        :return: string message
        """
        d = ""
        for c in msg:  # replace all chars outside BMP with a !
            d = d + (c if ord(c) < 0x10000 else '!')
        return d

    def publish_message(self, test_description, qos=1, retain=True):
        """
        This method publish the user message for a given test case.
        :param test_description: Topic name where user want to publish message
        :param qos: (Optional) The quality of service level to use, Default value 0
        :param retain: If set to true, the message will be set as the "last known
        good"/retained message for the topic.
        """
        publish_flag = True
        try:
            # get the parsing object according to the text case name and decide which sheet to be read
            parse_excel_file = ParseInputExcel(self.excel_file_path, sheet_name=test_description.split("_")[0])
            # get the topic name and message from excel file corresponding to give test case
            topic = parse_excel_file.get_topic_name(test_description=test_description)
            message = parse_excel_file.get_input_message(test_description=test_description)
            # Append the VIN DIN number in publish payload
            # Get the VIN DIN Number form configuration file
            robot_print_info(f"Publish Payload is {message}, type of payload: {type(message)}")
            message["vin"] = self.config_manager.get_tcu_vin_number()
            message["din"] = self.config_manager.get_tcu_din_number()
            robot_print_info(f"After append VIN, DIN, Publish Payload is {message}, type of payload: {type(message)}")
            return_code, msg_id = self.client.publish(topic=topic, payload=str(message), qos=qos, retain=retain)
            print("After publishing, return code = {}, message_id= {}".format(str(return_code), str(msg_id)))
            self.wait_for(self.client, MqttClass._MSG_TYPE_PUBACK)
            if msg_id == 0:
                robot_print_error("Unknown error to Publish the topic...!!!", print_in_report=True)
                # sys.exit()
            else:
                robot_print_info("Published...!!!", print_in_report=True)

        except ValueError as vlerr:
            robot_print_error("There is an error to publishing your topic, EXCEPTION: %s" % vlerr, print_in_report=True)

    def subscribe_topic(self, test_description: str):
        """
        This method is used to subscribe the give topic.
        :param test_description: Topic name to be subscribe
        """
        try:
            parse_excel_file = ParseInputExcel(self.excel_file_path, sheet_name=test_description.split("_")[0])
            # get the topic name fom excel file corresponding to give test case
            topic_name = parse_excel_file.get_topic_name(test_description)
            if "{vin}" in topic_name.lower():
                topic_name = topic_name.replace("{vin}", self.config_manager.get_tcu_vin_number())
            topics = [topic_name]
            print(f"Your are subscribing the topic: {topics}")
            if (self.mqtt_subscribe_topics(self.client, topics)) == -1:
                print("Can't subscribe quitting ")
                self.client.bad_connection_flag = True
                MqttClass._loopflag = False  # quit
            else:
                sub_status = self.wait_for(self.client, MqttClass._MSG_TYPE_CHKSUBS)
                if not sub_status:
                    print("Error to subscribe the topic")
        except ValueError as vlerr:
            print("Subscribe EXCEPTION: %s" % vlerr)

    def display_broker_response(self, time_stop: float = 10):
        """
        This method display the broker response.
        :param time_stop: Time to stop the network loop, Default value 10s
        """
        print("Inside Display")
        end_time = time.time() + time_stop
        try:
            while MqttClass._loopflag:
                now = time.time()
                self.client.loop(0.25)
                message_q = self.get_message_queue()
                print(f"Message Queue:: {message_q.qsize()}")
                while not message_q.empty():
                    m = message_q.get()
                    robot_print_debug(f"Broker Response: {m}", print_in_report=True)
                    MqttClass._BROKER_MESSAGES.put(m.split("MESSAGE:", 1)[1])
                    m = self.__convert(m)  # replace all chars outside BMP with a !
                    if len(str(m)) > 500:
                        print("Large Message Comes form Broker...!!!")
                    else:
                        self.__print_out(m)
                        # convert the response into Dictionary,
                        # TODO: Need to be check
                        if m.split("MESSAGE:", 1)[1] is not None:
                            try:
                                MqttClass._message_dict = json.loads(
                                    str(m.split("MESSAGE:", 1)[1].replace("'", "\"")))
                            except ValueError as vlerr:
                                print("ERROR %s" % vlerr, m.split("MESSAGE:", 1)[1], type(m.split("MESSAGE:", 1)[1]))
                                MqttClass._message_dict = {}
                                MqttClass._broker_response = m.split("MESSAGE:", 1)[1]
                        else:
                            MqttClass._message_dict = {}

                if self.client.disconnect_flag:
                    print("got disconnect so breaking loop")
                    MqttClass._loopflag = False
                if time_stop != 0 and now > end_time:  # stop the loop
                    print("Continue.....")
                    break
                    # UserMqttClass._loopflag = False

            robot_print_debug(f"total number of messages analysed= {self.get_message_count()}, "
                              f"displayed= {self.get_displayed_message_count()}", print_in_report=True)
        except ValueError as vlerr:
            robot_print_error(f"Error to validate the publish messages, EXCEPTION {vlerr}", print_in_report=True)

    def __print_out(self, msg):
        """
        Print the Broker response
        :param msg: message to be print
        """
        if display:
            print("\n", msg)

    def disconnect_client(self):
        """
        This method disconnect the client form the server.
        """
        if MqttClass._loopflag:
            MqttClass._loopflag = False

    def validate_broker_response(self, test_description: str, hygiene: bool = False, write_into_file: bool = False,
                                 file_path=None, itr_number: int = -1):
        """
        This method compare the broker response with expected output.
        It read the expected value form the user Input Excel file and compare this to broker response.
        :param test_description: Test case name which data to be read from the Input Excel file.
        :return: True if comparison success, Otherwise return False.
        """
        # TODO: Assuming that broker send a response message in a JSON format
        # Set a flag to get track the test result
        result = False
        vin_number = self.config_manager.get_tcu_vin_number()
        din_number = self.config_manager.get_tcu_din_number()
        cloud_output = {}
        # TODO: If Multiple response comes from the broker
        parse_excel_file = ParseInputExcel(self.excel_file_path, sheet_name=test_description.split("_")[0])
        # Check broker send any response or not
        if not MqttClass._BROKER_MESSAGES.empty():
            # Loop the Queue till the empty
            while not MqttClass._BROKER_MESSAGES.empty():
                print("Message Queue is ", MqttClass._BROKER_MESSAGES.qsize())
                # get the value from the broker payload
                value = MqttClass._BROKER_MESSAGES.get()
                # get the expected value -> dict value
                expected_output = parse_excel_file.get_expected_output(test_description=test_description)
                # get the cloud output
                if bool(value):
                    cloud_output = value.replace("\x00", "")
                    robot_print_debug(f"Cloud output: {cloud_output}")
                    try:
                        # convert the cloud response into JSON packet/Dictionary
                        cloud_output = json.loads(cloud_output)
                        print("cloud output is: ", cloud_output)
                        # initialize the Validate Response Class
                        validate_response = ValidateResponse()
                        # Check expected output or cloud output is empty or not
                        if expected_output != "" and cloud_output != "":
                            # Check the instance of expected and cloud output should be dictionary
                            if isinstance(cloud_output, dict) and isinstance(expected_output, dict):
                                if hygiene:
                                    robot_print_info(f"You are going to compare the hygiene payload,"
                                                     f"So we are just compare the VIN, DIN and keys of "
                                                     f"JSON payload not the values.")
                                    result = validate_response.validate_hygiene_payload(vin_num=vin_number,
                                                                                        din_num=din_number,
                                                                                        expected_payload=expected_output,
                                                                                        cloud_output=cloud_output,
                                                                                        write_to_file=write_into_file,
                                                                                        file_path=file_path,
                                                                                        itr_num=itr_number
                                                                                        )
                                else:
                                    result = validate_response.validate_response(vin_number=vin_number,
                                                                                 din_number=din_number,
                                                                                 expected_output=expected_output,
                                                                                 cloud_output=cloud_output)
                                    if result:
                                        robot_print_info(f"Expected Payload received")
                                        break
                            else:
                                # if expected output or cloud output is empty
                                robot_print_error(
                                    f"It seems either expected output or cloud response "
                                    f"not in proper Dictionary format. "
                                    f"Please check the response. "
                                    f"\nExpected Output: {expected_output} "
                                    f"\nCloud Output: {cloud_output}",
                                    print_in_report=True)
                        else:
                            robot_print_error(
                                f"It seems either expected output or cloud response empty. "
                                f"Please check the response. "
                                f"\nExpected Output: {expected_output} "
                                f"\nCloud Output: {cloud_output}",
                                print_in_report=True)
                    except json.JSONDecodeError as json_decode_error:
                        robot_print_error(f"Cloud response in not proper JSON format {json_decode_error}",
                                          print_in_report=True)
                        MqttClass._comparision_result.append(cloud_output)
                else:
                    robot_print_error("There is no JSON packet response send by the broker...!!!",
                                      print_in_report=True)
                    print("The Response send by Broker : {}".format(MqttClass._broker_response))
        else:
            robot_print_error(f"Queue is Empty, No response comes from broker...!!!")
            cloud_output = "No response Comes from broker...!!!"

        # Total response comes from the broker
        print("Total responses are : ", MqttClass._comparision_result)
        # set the broker response output into the Input Excel File
        parse_excel_file.set_test_output(test_description=test_description, value=str(cloud_output))

        # set the comparison output into Input excel file
        if result:
            parse_excel_file.set_test_result_status(test_description=test_description, status="PASS")
            return True
        else:
            parse_excel_file.set_test_result_status(test_description=test_description, status="FAIL")
            return False

    def get_message_dic(self):
        robot_print_debug(f"{MqttClass._message_dict}", print_in_report=True)

    def unsubscribe_topic(self, test_description):
        """
        This method is used to unsubscribe the topic.
        :param test_description: provide the test description from Excel Sheet.
        :return: None
        """
        try:
            parse_excel_file = ParseInputExcel(self.excel_file_path, sheet_name=test_description.split("_")[0])
            # get the topic name fom excel file corresponding to give test case
            topics = [parse_excel_file.get_topic_name(test_description)]
            if (self.mqqt_unsubscribe_topic(self.client, topics)) == -1:
                print("Can't unsubscribe quitting ")
                self.client.bad_connection_flag = True
                MqttClass._loopflag = False  # quit
            else:
                sub_status = self.wait_for(self.client, MqttClass._MSG_TYPE_CHKSUBS)
                if not sub_status:
                    print("Error to unsubscribe the topic")
        except ValueError as vlerr:
            robot_print_debug(f"unSubscribe EXCEPTION: {vlerr}")
