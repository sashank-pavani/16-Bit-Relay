from datetime import datetime
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.Vautokit import VautokitAPI
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.CANInputFileParsing.CanInputFileParsing import \
    CanInputFileParsing
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.Vautokit import PCF8575
from Robo_FIT.GenericLibraries.GenericOpLibs.VAutoKit.Vautokit import INA291
import threading
import time


# Dictionary to hold references to message senders and their data


class VAutoKitClass:
    """
        This Class is used for VAutoKitClass for Relay connect and Send CAN signal using vAutoKit.
    """
    __task_id_counter = 1
    __message_senders = {}
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VAutoKitClass, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, channel_name='single'):
        if not hasattr(self, 'initialized'):
            self.config_manager = ConfigurationManager()
            self.read_input_file_data = CanInputFileParsing(channel_name)
            self.autokit_init()
            self.initialized = True

    def get_shuntvoltage_mv(self):
        """
                This method is used to get Shunt Voltage in milli volt using VAutokit current sensor
        """
        try:
            value = INA291.getShuntVoltage_mV()
            return value
        except Exception as exp:
            robot_print_error(f"Exception on get shunt voltage-{exp}")

    def get_busvoltage_mv(self):
        """
                        This method is used to get bus Voltage in milli volt using VAutokit current sensor
        """
        try:
            value = INA291.getBusVoltage_mV()
            return value
        except Exception as exp:
            robot_print_error(f"Exception on get bus voltage-{exp}")

    def get_power_mw(self):
        """
                        This method is used to get power in milli watts using VAutokit current sensor
        """
        try:
            value = INA291.getPower_mW()
            return value
        except Exception as exp:
            robot_print_error(f"Exception on get power-{exp}")

    def get_current_ma(self):
        """
                        This method is used to get current in milli amps using VAutokit current sensor
        """
        try:
            value = INA291.getCurrent_mA()
            return value
        except Exception as exp:
            robot_print_error(f"Exception on get current-{exp}")


    def relay_16_setdir(self, relay: str):
        """
                        This method is used to set direction 16 pin relay
                        param relay: Relay name from Robot script provided by user for to connect relay
                        """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            status = PCF8575.set_dio_dir(int(idx), PCF8575.DIO_DIR_OUT)
            #time.sleep(5)
            # robot_print_info(f"Relay_16_dir status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on set dir relay_16{relay}-{exp}")
            return False

    def relay_16_push(self, relay: str):
        """
                         This method is used to set direction 16 pin relay
                         param relay: Relay name from Robot script provided by user for to connect relay
                         """
        try:
            idx = self.config_manager.get_relay_no(relay)

            robot_print_info(f"idx relay value- {idx}")
            # PCF8575.PCF8575_init(0x20)
            # status = PCF8575.set_dio_val_50ms(int(idx), PCF8575.DIO_VAL_LOW)
            status = PCF8575.set_dio_val(int(idx), PCF8575.DIO_VAL_LOW)
            time.sleep(400/1000)
            status = PCF8575.set_dio_val(int(idx), PCF8575.DIO_VAL_HIGH)
            robot_print_info(f"Relay_push status- {status}")
            # time.sleep(10)
            # robot_print_info(f"Relay_push status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on push relay_16{relay}-{exp}")
            return False

    def relay_16_connect1(self, relay: str):
        """
                This method is used to connect 16 pin relay
                param relay: Relay name from Robot script provided by user for to connect relay
                """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            status = PCF8575.set_dio_val(int(idx), PCF8575.DIO_VAL_LOW)
            robot_print_info(f"Relay_16_connect status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on connect relay_16{relay}-{exp}")
            return False

    def relay_16_connect(self, relay: str):
        """
                This method is used to connect 16 pin relay
                param relay: Relay name from Robot script provided by user forturnleft to connect relay
                """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            status = PCF8575.set_dio_val(int(idx), PCF8575.DIO_VAL_LOW)
            # robot_print_info(f"Relay_16_connect status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on connect relay_16{relay}-{exp}")
            return False

    def relay_16_disconnect(self, relay: str):
        """
                        This method is used to disconnect 16 pin relay
                        param relay: Relay name from Robot script provided by user for to connect relay
                        """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            status = PCF8575.set_dio_val(int(idx), PCF8575.DIO_VAL_HIGH)
            # robot_print_info(f"Relay_16_disconnect status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on disconnect relay_16{relay}-{exp}")
            return False

    def relay_connect(self, relay: str):
        """
        This method is used to connect relay
        param relay: Relay name from Robot script provided by user for to connect relay
        """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            time.sleep(5)
            status = VautokitAPI.set_relay(int(idx), 1)
            robot_print_info(f"Relay_connect status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Exception on connect relay{relay}-{exp}")
            return False

    def relay_connect_time(self, relay: str):
        """
        This method is used to connect relay
        param relay: Relay name from Robot script provided by user for to connect relay
        """
        try:
            if self.config_manager.get_relay_no(relay)!= None:
                idx = self.config_manager.get_relay_no(relay)
                robot_print_info(f"idx relay value- {idx}")
                status = VautokitAPI.set_relay(int(idx), 1)
                if status == 1:
                    timestamp = datetime.now().strftime("%H%M%S.%f")
                    return timestamp
                else:
                    return False

        except Exception as exp:
            robot_print_error(f"Exception on connect relay{relay}-{exp}")
            return False


    def relay_disconnect(self, relay: str):
        """
        This method is used to disconnect relay
        param relay: Relay name from Robot script provided by user for to connect relay
        """
        try:
            idx = self.config_manager.get_relay_no(relay)
            robot_print_info(f"idx relay value- {idx}")
            status = VautokitAPI.set_relay(int(idx), 0)
            # time.sleep(1)
            #robot_print_info(f"Relay_disconnect status- {status}")
            if status == 1:
                return True
            else:
                return False
        except Exception as exp:
            robot_print_error(f"Unable to disconnect relay{relay}-{exp}")
            return False

    def can_init(self):
        """
        This method is used to Initialize Vautokit CAN
        """
        try:
            speed = self.config_manager.get_speed()
            VautokitAPI.can_init(int(speed))
            time.sleep(1)

        except Exception as exp:
            robot_print_error(f"Exception on initialize vautocan-{exp}")

    def send_vautocan_signal(self, can_des: str, signal_type: str = "TX"):
        """
        This method is used to send Vautokit CAN signal
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file.
        """
        try:
            message_name = self.read_input_file_data.get_can_message_name(can_des=can_des, signal_type=signal_type)
            if message_name is not None:
                can_message = self.read_input_file_data.get_msg_object_by_msg_name(message_name=message_name)
                user_data = self.read_input_file_data.get_can_data(can_des=can_des, signal_type=signal_type)
                robot_print_debug(f"vAutokit can message : - {can_message}")
                VautokitAPI.can_tx(can_message.frame_id, user_data)
            else:
                robot_print_error("Error message name is none")
        except Exception as exp:
            robot_print_error(f"unable to send can signal - {exp}")

    def __canRxCallback(self, data):
        id = data[1] << 8 | data[2]

    def can_rx_mon_enable(self):
        """
        This method will enable can_rx
        """
        try:
            VautokitAPI.can_rx_mon_enable(1, self.__canRxCallback)
            time.sleep(2)
        except Exception as exp:
            robot_print_error(f"Exception on activate RX - {exp}")

    def can_rx_mon_disable(self):
        """
        This method will disable can_rx
        """
        try:
            VautokitAPI.can_rx_mon_enable(0)
            time.sleep(2)
        except Exception as exp:
            robot_print_error(f"Exception on deactivate RX - {exp}")

    def __vautocan_trace_file_name(self) -> str:
        """
        This method check for the file name
        If filename is correct which is provided by the user in config file
        then it returns that filename otherwise it uses default file name
        i.e. can_trace.asc
        :return: Filename if correct name provided by user otherwise default
                `can_trace.asc`
        """
        try:
            file_name = self.config_manager.get_vautocan_trace_file_name()
            file_datetime = datetime.now().strftime("_%d_%b_%Y_%H_%M_%S")
            # file_name = file_name.split(".")[0] + file_datetime + "." + file_name.split(".")[1]
            file_name = self.config_manager.get_vautocan_trace_file_path(file_name)
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
                f_name = "vauto_can_trace" + file_datetime + ".asc"
                default_file_name = self.config_manager.get_vautocan_trace_file_path(f_name)
                return default_file_name
        except Exception as exp:
            robot_print_error(f" EXCEPTION Occurred: {exp}")

    def autokit_init(self):
        """
        This method use to initialize vAutoKit using port in the config file
        """
        try:
            COM = self.config_manager.get_serial_port()
            #COM = 'COM7'
            robot_print_info(f"The com port connect - {COM}")
            log_file = self.__vautocan_trace_file_name()
            VautokitAPI.init(COM, log_file)
            PCF8575.PCF8575_init(0x20)
            INA291.INA291_init(0x40)
        except Exception as exp:
            robot_print_error(f" EXCEPTION Occurred: {exp}")

    def __send_vautocan_message(self, can_id, data, interval, stop_event):
        try:
            while not stop_event.is_set():
                CMD_CAN = VautokitAPI.can_tx(can_id, data)
                time.sleep(interval)
        except Exception as exp:
            robot_print_error(f" EXCEPTION Occurred: {exp}")

    def send_vautocan_signal_periodically(self, can_des: str, signal_type: str = "TX", periodicity: int = 100):
        """
        This method is used to send Vautokit CAN signal Periodically
        :param signal_type: Type of the signal i.e. TX,"RX", "MASTER"
        :param can_des: CAN Description in Input Excel file
        :param periodicity: Periodic time provided by user in Milisecond in case not provided in input file
        """
        try:
            message_name = self.read_input_file_data.get_can_message_name(can_des=can_des, signal_type=signal_type)
            if message_name is not None:
                can_message = self.read_input_file_data.get_msg_object_by_msg_name(message_name=message_name)
                user_data = self.read_input_file_data.get_can_data(can_des=can_des, signal_type=signal_type)
                can_id = can_message.frame_id
                if can_message.cycle_time is not None:
                    interval = int(can_message.cycle_time) / 1000
                    robot_print_info(f"periodic_time-{interval}")
                else:
                    robot_print_warning(
                        f"There is not cycle time provided in dbc file for message: {can_message.name}, "
                        f"So setting cycle time as: {periodicity}ms", print_in_report=True, underline=True)
                    interval = int(periodicity) / 1000
                try:
                    for task_id, sender_info in VAutoKitClass.__message_senders.items():
                        if 'can_id' in sender_info and sender_info['can_id'] == can_id:
                            # Update the data for the existing task
                            sender_info['data'] = user_data
                            return task_id  # Return the existing task ID
                    task_id = VAutoKitClass.__task_id_counter  # Assign the current task ID
                    VAutoKitClass.__task_id_counter += 1  # Increment the task ID counter
                    # Create and start a new sender if it doesn't exist
                    stop_event = threading.Event()
                    thread = threading.Thread(
                        target=self.__send_vautocan_message,
                        args=(can_id, user_data, interval, stop_event)
                    )
                    # Create a dictionary for the sender with data and stop event
                    VAutoKitClass.__message_senders[can_id] = {
                        'data': user_data,
                        'stop_event': stop_event,
                        'thread': thread
                    }
                    # Start the sender thread
                    thread.start()
                    # thread.join()
                    VAutoKitClass.__message_senders[task_id] = {'thread': thread, 'stop_event': stop_event,
                                                                'can_id': can_id}

                    return task_id  # Return the task ID

                except Exception as exp:
                    robot_print_error(f"exception found on e-{exp}")

        except Exception as exp:
            robot_print_error(f"exception found on e-{exp}")

    def stop_vautocan_periodically(self, task_id):
        """
        This method is used to stop the periodic message.
        :param task_id: Particular thread will get stop based on the task id
        """
        try:
            if task_id in VAutoKitClass.__message_senders:
                sender_info = VAutoKitClass.__message_senders[task_id]
                sender_info['stop_event'].set()
                # sender_info['thread'].join()
                del VAutoKitClass.__message_senders[task_id]

        except Exception as exp:
            robot_print_error(f"exception found on e-{exp}")

    def stop_vautocan_trace(self):
        """
        This method will stop the trace
        """
        VautokitAPI.stop_trace = True
        robot_print_info(f"The vAutoKit stop triggered")

# obj = VAutoKitClass()
# obj.getCurrent_mA()