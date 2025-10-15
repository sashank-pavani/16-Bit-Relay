import can
import time
import logging
import threading
from datetime import datetime
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class FirstCanSignal:

    def __init__(self):
        # Generate log file name with timestamp
        # self.timestamp = datetime.now().strftime("%Y  %m%d_%H%M%S")
        # self.log_filename = f"C:\\can_trace\\can_trace_{self.timestamp}.log"
        #
        # # Configure logging to capture all CAN traffic, including errors
        # logging.basicConfig(
        #     filename=self.log_filename,
        #     filemode="w",
        #     format="%(asctime)s - %(message)s",
        #     level=logging.INFO
        # )
        self.a=[]
        self.stop_event = threading.Event()
        self.start_flag = 0
        self.rx_start_flag = 0
        self.common_keyword = CommonKeywordsClass()
        #self.first_tx_time
    def setup_can_interface(self, channel=0, bitrate=500000, fd_bitrate=2000000):
        """Setup Vector CAN FD interface."""
        try:
            bus = can.Bus(interface="vector", channel=channel, bitrate=bitrate, fd=True, data_bitrate=fd_bitrate, receive_own_messages=True)
            print(f"Connected to Vector CAN FD channel {channel} at {bitrate} bps / {fd_bitrate} bps")
            logging.info(f"Connected to Vector CAN FD channel {channel} at {bitrate} bps / {fd_bitrate} bps")
            return bus
        except Exception as e:
            print(f"Error setting up CAN interface: {e}")
            logging.error(f"Error setting up CAN interface: {e}")
            return None

    def send_periodic_can_fd_message(self, bus, arbitration_id, data, interval=0.01):
        """Send CAN FD message periodically every 'interval' seconds until stop_event is set."""
        def send_loop():

            while not self.stop_event.is_set():
                try:
                    msg = can.Message(arbitration_id=arbitration_id, data=data, is_fd=True)
                    bus.send(msg)
                    log_msg = f"Sent: ID={hex(arbitration_id)}, Data={list(data)}, DLC={msg.dlc}, Type=CAN FD"
                    print(log_msg)
                    logging.info(log_msg)
                    self.start_flag = self.start_flag + 1
                    if self.start_flag == 1:
                        now = datetime.now()
                        #self.tx_timee = datetime.now().strftime("%d_%b_%Y_%H_%M_%S")
                        #self.tx_timee = now.strftime("%d_%b_%Y_%H_%M_%S") + f"_{now.microsecond // 1000:03d}"
                        self.tx_timee = now.strftime("%H%M%S.%f")
                        robot_print_info(f"tx_time = {self.tx_timee}")
                    time.sleep(interval)

                except can.CanError as e:
                    print(f"Failed to send message: {e}")
                    logging.error(f"Send error: {e}")

        thread = threading.Thread(target=send_loop, daemon=True)
        thread.start()

    def log_can_messages(self, bus):
        timestamp = datetime.now().strftime("%H%M%S.%f")
        log_filename = f"C:\\can_trace\\can_trace_FCM_1stCAN.asc"
        logging.basicConfig(
            filename=log_filename,
            filemode="w",
            format="%(asctime)s - %(message)s",
            level=logging.INFO
        )
        """Continuously log received CAN and CAN FD messages."""
        print("Logging CAN messages...")

        while not self.stop_event.is_set():
            msg = bus.recv(timeout=0.01)
            if msg:
                msg_type = "CAN FD" if msg.is_fd else "Classical CAN"
                log_msg = f"Received: ID={hex(msg.arbitration_id)}, DLC={msg.dlc}, Data={list(msg.data)}, Type={msg_type}"
                print(log_msg)
                logging.info(log_msg)
                self.rx_start_flag = self.rx_start_flag + 1
                if self.rx_start_flag == 1:
                    now = datetime.now()
                    #self.rx_time = datetime.now().strftime("%d_%b_%Y_%H_%M_%S_%F")
                    #self.rx_time = now.strftime("%d_%b_%Y_%H_%M_%S") + f"_{now.microsecond // 1000:03d}"
                    self.rx_time = now.strftime("%H%M%S.%f")
                    robot_print_info(f"rx_time = {self.rx_time}")

                if msg.is_error_frame:
                    print(f" NACK Error detected: ID={hex(msg.arbitration_id)}")
                    logging.warning(f"NACK Error detected: ID={hex(msg.arbitration_id)}")

    def calculate_time_difference(self, time1, time2, time_format="%H%M%S.%f"):
        # Convert the time strings to datetime objects
        datetime1 = datetime.strptime(time1, time_format)
        datetime2 = datetime.strptime(time2, time_format)
        robot_print_info(f"datetime1 == {datetime1} datetime2 == {datetime1}")
        # Calculate the difference
        #time_difference = datetime2 - datetime1
        time_difference = datetime1 - datetime2

        # Extract total seconds and microseconds
        total_seconds = time_difference.total_seconds()
        robot_print_info(f"returned value {total_seconds:.6f}")
        return f"{total_seconds:.6f}"


    def stop(self):
        """Stop CAN operations gracefully."""
        print("Stopping CAN operations...")
        logging.info("Stopping CAN operations...")
        self.stop_event.set()

    def extract_datetime_from_filename_new(self,filename):
        # Extract timestamp components from the filename
        parts = filename.split('_')
        time_str = parts[2]  # HHMMSS
        microseconds_str = parts[3].split('.')[0]  # Extract only numeric part before .jpg

        # Combine time and microseconds into a single string
        time_with_microseconds_str = f"{time_str}.{microseconds_str}"

        try:
            # Convert the string to a datetime object
            timestamp = datetime.strptime(time_with_microseconds_str, "%H%M%S.%f")

            # Format the datetime object to the desired string format
            formatted_time = timestamp.strftime("%H%M%S.%f")

            return formatted_time
        except ValueError as e:
            print(f"Error parsing time: {e}")
            return None

    def measure_first_can_message(self):

        # Generate log file name with timestamp
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #timestamp = datetime.now().strftime("%d_%b_%Y_%H_%M_%S")
        timestamp = datetime.now().strftime("%H%M%S.%f")
        #log_filename = f"C:\\can_trace\\can_trace_FCM_new_impl.asc"
        # log_filename = f"tasc"
        log_filename = os.path.join(self.common_keyword.get_report_path(), "CAN_TRACE",
                                   f"can_trace_firstcan_{timestamp}.log")
								   

        # Configure logging
        logging.basicConfig(
            filename=log_filename,
            filemode="w",
            format="%(asctime)s - %(message)s",
            level=logging.INFO, force=True
        )
        print("START")
        can_bus = self.setup_can_interface(channel=0, bitrate=500000)
        print("START")
        if can_bus:
            # Start periodic CAN FD message sending (10ms interval)
            self.send_periodic_can_fd_message(can_bus, arbitration_id=0x620, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00], interval=0.003)

            # Start message logging in a separate thread
            log_thread = threading.Thread(target=self.log_can_messages, args=(can_bus,))
            log_thread.start()

            # Run for 20 seconds
            time.sleep(20)
            self.stop()

            # Wait for logging thread to finish
            log_thread.join()

            # Shutdown CAN interface
            can_bus.shutdown()
            print("CAN interface shut down.")
            try:
                robot_print_info(f"Tx time = {self.tx_timee}")
                robot_print_info(f"Rx time = {self.rx_time}")
                return self.tx_timee, self.rx_time
            except Exception as e:
                robot_print_error("Issue in TX and RX time")

    def list_append(self, *values):
        self.a.extend(values)
        return self.a

    def find_min(self):
        if not self.a:
            return None  # or raise an exception if preferred
        return min(self.a)

    def clear_list(self):
        self.a.clear()
        return self.a


if __name__ == "__main__":
    h= FirstCanSignal()
    h.measure_first_can_message()