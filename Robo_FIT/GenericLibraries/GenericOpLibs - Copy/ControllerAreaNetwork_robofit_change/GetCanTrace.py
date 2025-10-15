from datetime import datetime, timedelta
from time import sleep
from can import Logger, BusABC, CanError, Message
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.TimedRotatingFilelogger import TimedRotatingFilelogger
import concurrent.futures
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info, \
    robot_print_debug
import threading

global exit_loop


class GetCanTrace:
    """
    This Class use for Get CAN traces
    """
    exit_loop = 0
    _instances = {}
    _file_names = {}
    _lock = threading.Lock()  # Lock for thread-safe operations

    @staticmethod
    def get_can_log_instance(can_bus: BusABC, file_name: str) -> 'GetCanTrace':
        with GetCanTrace._lock:
            instance = GetCanTrace._instances.get(can_bus)

            if instance is None:
                instance = GetCanTrace(can_bus=can_bus, file_name=file_name)
                GetCanTrace._instances[can_bus] = instance

            return instance

    def __init__(self, can_bus: BusABC, file_name: str = ".asc"):
        self.can_logger = None
        self.can_bus = can_bus
        self.__trace_calling = False
        self.__all_stop_can_trace = 0
        self.__list = []

        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.__list_lock = threading.Lock()  # Lock for list operations

        with GetCanTrace._lock:
            if can_bus not in GetCanTrace._file_names:
                GetCanTrace._file_names[can_bus] = file_name

            self.file_name = GetCanTrace._file_names[can_bus]

    def __get_all_can_trace(self):

        try:
            # breakpoint()
            if (self.can_logger is not None) and (GetCanTrace.exit_loop == 0):
                robot_print_info(f"can_bus === {self.can_bus}")
                for msg in self.can_bus:
                    robot_print_info(f"msg === {msg}")
                    if GetCanTrace.exit_loop == 0:
                        if msg is not None:
                            self.can_logger.on_message_received(msg)

                            with self.__list_lock:
                                if self.__all_stop_can_trace:
                                    self.__list = []
                                else:
                                    self.__list.append(msg)
                            # breakpoint()
                            if self.__all_stop_can_trace:
                                robot_print_info(f"Stopping CAN trace for {self.file_name}")
                                self.__all_stop_can_trace = 0
                                GetCanTrace.exit_loop = 1

                                self.can_logger.stop()
                                break

                    else:
                        break

            else:
                return CanError("CAN Logger is initialized as None")

        except CanError as can_error:
            robot_print_error("There is an error getting the trace, EXCEPTION: %s" % can_error)

    def get_all_trace(self) -> Logger:
        try:
            if not self.__trace_calling:
                self.can_logger = Logger(self.file_name)
                robot_print_debug(f"Start getting CAN logs for {self.file_name}")

                self.executor.submit(self.__get_all_can_trace)

                self.__trace_calling = True
                return self.can_logger

        except Exception as exp:
            self.can_logger.stop()
            robot_print_debug(f"Error running concurrent feature for {self.file_name}: {exp}")

    def time_rotate_logs(self, when, interval, backup_count) -> TimedRotatingFilelogger:
        try:
            if not self.__trace_calling:
                self.can_logger = TimedRotatingFilelogger(self.file_name, when=str(when),
                                                          interval=int(interval), backupCount=int(backup_count))
                robot_print_debug("start getting can logs")

                self.executor.submit(self.__get_all_can_trace)

                self.__trace_calling = True
                return self.can_logger
        except Exception as exp:
            self.can_logger.stop()
            robot_print_debug("Error to run concurrent Feature as EXCEPTION: %s" % exp)

    def stop_can_trace(self):
        with self.__list_lock:
            self.__all_stop_can_trace = 1

        robot_print_info("Stopping CAN trace...")

    def get_message_data(self, can_message: Message, timeout: float):
        end_time = datetime.now() + timedelta(seconds=timeout)
        while end_time > datetime.now():
            with self.__list_lock:
                # for msg in self.__list:
                #     if msg.arbitration_id == can_message.arbitration_id and msg.is_rx:
                #         robot_print_debug(f" thread true msg while verification {msg}")
                #
                #         robot_print_debug(f" thread true msg while verification {self.__list}")
                #         breakpoint()
                #         return msg.data

                recent_msg = None

                # Iterate through the list in reverse order to find the most recent message
                for msg in reversed(self.__list):
                    if msg.arbitration_id == can_message.arbitration_id and msg.is_rx:
                        recent_msg = msg
                        break  # Exit loop as soon as we find the most recent valid message

                if recent_msg:
                    robot_print_debug(f"Most recent valid message found: {recent_msg}")
                    return recent_msg.data
                else:
                    robot_print_debug("No valid message found")
                    return None

        robot_print_debug(f"{self.__list} thread did not find matching can msg within timeout")
        return None

    def make_list_empty(self):
        with self.__list_lock:
            self.__list = []

    def shutdown(self):
        """Shutdown method for clean-up."""

        self.stop_can_trace()
        GetCanTrace.exit_loop = 1
