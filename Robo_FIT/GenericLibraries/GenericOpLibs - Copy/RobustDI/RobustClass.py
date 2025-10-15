import time
import cv2
import threading
import keyboard
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_info, robot_print_warning
from Robo_FIT.GenericLibraries.GenericOpLibs.ProgrammablePowerSupply.PpsClass import PpsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork import CanClass
from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting import ImageFinder
from Robo_FIT.GenericLibraries.GenericOpLibs.RobustDI.ConfigurationManager import ConfigurationManager
from datetime import datetime
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *


class RobustClass:
    """
        This Class is to ensure the behaviour of cluster while in Sleep wake up and power cycle.
    """


    # prepare to exit the program
    def quit(self):
        #global exitProgram
        robot_print_debug(f"\n\n\n\n\n\nn*******************hot key q pressed *************\n\n\n\n\n\n\n\n")
        #print ("*******************hot key q pressed *************")
        self.exitProgram = True

    def __init__(self, channel_name):
        self.duration = None
        self.output_file = None
        self.robust_pps = None
        self.robust_can = CanClass.CanClass(channel_name)
        self.common_keywords = CommonKeywordsClass()
        self.recording = False
        self.capture_thread = None
        self.video_writer = None
        self.global_screenshot_on = False
        self.global_screenshot_off = False
        self.stop_recording_event = threading.Event()
        self.config_manager = ConfigurationManager()
        self.path1 = self.__cam_image_file_name()
        self.path2 = self.__cam_image_file_name_off()
        self.project_config = ProjectConfigManager()
        self.exitProgram = False
        # path is "Project_W601/res/Images/"
        self.image_template_path = os.path.join(self.common_keywords.get_root_path(),
                                                PROJECT,
                                                CRE_LIBRARIES, CRE_RESOURCES, CRE_IMAGES)
        self.image_finder = ImageFinder.ImageFinder()

    def __cam_image_file_name(self):
        """
        This Method Creates an Image file with the given name in config file when cluster is on Condition
        :return : file name of the image
        """
        file_name = self.config_manager.get_image_name()
        file_name = self.config_manager.get_image_screenshot_path(file_name)
        if file_name.endswith(".jpg"):
            return file_name
        elif file_name.endswith(".png"):
            return file_name
        elif file_name.endswith(".bmp"):
            return file_name
        else:
            robot_print_warning(f"Unknown file name ({file_name}) for the IMAGE"
                                f" File name, So we are using default file name i.e. wake_cap.jpg")
            f_name_on = "wake_cap" + ".jpg"
            default_file_name = self.config_manager.get_image_screenshot_path(f_name_on)
            return default_file_name

    def __cam_image_file_name_off(self):
        """
        This Method Creates an Image file with the given name in config file when cluster is off Condition
        :return : file name of the image
        """
        file_name1 = self.config_manager.get_image_name_off()
        file_name = self.config_manager.get_image_screenshot_path(file_name1)
        if file_name.endswith(".jpg"):
            return file_name
        elif file_name.endswith(".png"):
            return file_name
        elif file_name.endswith(".bmp"):
            return file_name
        else:
            robot_print_warning(f"Unknown file name ({file_name}) for the IMAGE"
                                f" File name, So we are using default file name i.e. sleep_cap.jpg")
            f_name_off = "sleep_cap" + ".jpg"
            default_file_name = self.config_manager.get_image_screenshot_path(f_name_off)
            return default_file_name

    def robust_sleep_wakeup(self, delay_wakeup, delay_sleep, timer, CAN_AWAKE, CAN_SLEEP, CAN_PARK):
        """
        This method is Robustness test for sleep wakeup
        :param delay_wakeup:delay_wakeup value from Robot script provided by user for delay in msec
        :param delay_sleep:delay_sleep value from Robot script provided by user for delay in msec
        :param timer: User can define n number of times and "inf" to run infinity times
        :param CAN_AWAKE: CAN_AWAKE is a can description for wake up signal from Robot script provided by the user
        :param CAN_SLEEP: CAN_SLEEP is a can description for sleep signal from Robot script provided by the user
        :param CAN_PARK: CAN_PARK is a can description for park signal from Robot script provided by the user
        :return: True if No failure detection
        :return: False If failure detection
        """
        try:
            avg_curr_high = self.config_manager.get_current_high()
            avg_curr_low = self.config_manager.get_current_high()
            loop = 1
            delay_x = int(delay_wakeup)
            delay_y = int(delay_sleep)

            """if user provided inf the loop executes infinity time"""
            if timer != 'inf':
                robot_print_debug(f"int(timer) > loop::{int(timer) > loop}")
                timer = int(timer)
            else:
                timer = float('inf')
            robot_print_debug(f"condition::{timer}")
            pps = PpsClass()
            while timer >= loop:
                robot_print_info(f"Cycle count::{loop}")
                self.robust_can.send_can_signal_periodically(CAN_AWAKE)
                sleep(delay_x)
                chk_current_bs = pps.get_current_value()
                robot_print_info(f"Check current increased or not current value-:{chk_current_bs}")
                if chk_current_bs > float(avg_curr_high):
                    robot_print_info(f"Current Increased in wakeup condition:- successfully verified ")
                    self.global_screenshot_on = True
                    time.sleep(5)
                    value_awake = self.robust_can.get_rx_message()
                    if not value_awake:
                        robot_print_error("Failure Detection 1: RX message not found in wakeup condition")
                        self.stop_recording()
                        return False
                    else:
                        robot_print_info("RX message found -  Satisfied No Failure Detected")
                    path1 = self.path1
                    path2 = os.path.join(self.image_template_path, self.config_manager.get_template_image_name())
                    result = self.image_finder.is_img_in_img(path1, path2)
                    if result:
                        robot_print_info("Check the display whether cluster is on -  Satisfied no Failure Detected")
                    else:
                        robot_print_error("Failure Detection 2: Display not found")
                        return False

                    task1 = self.robust_can.send_can_signal_periodically(CAN_SLEEP)
                    task2 = self.robust_can.send_can_signal_periodically(CAN_PARK)
                    self.robust_can.stop_can_periodically_signal(task1)
                    self.robust_can.stop_can_periodically_signal(task2)
                else:
                    robot_print_error(f"Current not Increased in wakeup condition:- Execution Getting stopped")
                    self.stop_recording()
                    return False
                sleep(delay_y)
                chk_current_as = pps.get_current_value()
                robot_print_info(f"check current decreased or not current value-:{chk_current_as}")

                if chk_current_as < float(avg_curr_low):
                    robot_print_info("Current decreased in sleep condition:- successfully verified ")
                    self.global_screenshot_off = True
                    time.sleep(5)
                    value_sleep = self.robust_can.get_rx_message()
                    if value_sleep:
                        robot_print_error("Failure Detection 3: Detected RX message in sleep condition")
                        self.stop_recording()
                        return False
                    else:
                        robot_print_info("No RX message in Sleep Condition -  Satisfied No failure detected")
                    path3 = self.path2
                    result = self.image_finder.is_img_in_img(path3, path2)
                    if result:
                        robot_print_error("Failure Detection 4: Display found")
                        self.stop_recording()
                        return False
                    else:
                        robot_print_info("Check the display whether cluster is off -  Satisfied no failure detected")
                        pass
                    time.sleep(5)
                    loop = loop + 1
                else:
                    robot_print_error(f"Current not decreased in sleep condition:- Execution getting stopped")
                    self.stop_recording()
                    return False
            return True

        except Exception as e:
            robot_print_error(f"Some exception found :- {e}")

        finally:
            robot_print_info("Video recording stopped.")
            self.stop_recording()

    def start_recording(self, output_file, duration):
        """
        The start recording method will trigger the video recording
        :param output_file: output_file is the name of the video file
        :param duration: The duration of the video interval
        :return: None
        """
        if not self.recording:
            self.recording = True
            self.output_file = output_file
            self.duration = duration
            self.capture_thread = threading.Thread(target=self._capture_frames)
            # time.sleep(1)
            self.capture_thread.start()
            # time.sleep(1)
            robot_print_info("Video recording started.")

    def stop_recording(self):
        """
        The stop recording method will stop the video recording
        :return : None
        """
        robot_print_info(f"Stop video triggered")
        if self.recording:
            self.recording = False
            self.stop_recording_event.set()
            self.capture_thread.join()
            # self.video_writer.release()
            self.video_writer = None
            # self.capture_thread.stop()
            robot_print_info("Video recording stopped.")
            # return

    def _capture_frames(self):
        """
        The capture frames method will capture the video and screenshot
        """
        try:
            robot_print_info(f"self.duration: {self.duration}")
            video_capture = cv2.VideoCapture(0)

            # Set the video recording parameters
            output_fps = 30.0
            output_codec = cv2.VideoWriter_fourcc(*"mp4v")
            frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            segment_count = 0
            delay_count = 1
            while True:

                video_name = f'video_{self.output_file}_{segment_count}.mp4'
                cropped_screenshot_path = self.config_manager.get_image_screenshot_path(video_name)

                output_video = cv2.VideoWriter(cropped_screenshot_path, output_codec, output_fps,
                                               (frame_width, frame_height))
                start_time = cv2.getTickCount()

                while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < float(self.duration):
                    # Read a frame from the video capture
                    video_names = f'video_{self.output_file}_{segment_count - 1}.mp4'
                    cropped_screenshot_path1 = self.config_manager.get_image_screenshot_path(video_names)
                    if os.path.exists(cropped_screenshot_path1):
                        os.remove(cropped_screenshot_path1)
                    ret, frame = video_capture.read()

                    # Check if the frame was successfully read
                    if not ret:
                        break

                    if self.global_screenshot_on:
                        screenshot_path = self.path1
                        cv2.imwrite(screenshot_path, frame)
                        robot_print_info(f"Screenshot taken: {screenshot_path}")
                        self.global_screenshot_on = False

                    if self.global_screenshot_off:
                        screenshot_path = self.path2
                        cv2.imwrite(screenshot_path, frame)
                        robot_print_info(f"Screenshot taken: {screenshot_path}")
                        self.global_screenshot_off = False

                    output_video.write(frame)

                delay_count += 1
                # Release the current video writer
                output_video.release()
                segment_count += 1

                if self.stop_recording_event.is_set():
                    break

            # Release the video capture object and close the window
            cv2.destroyAllWindows()
            robot_print_info("Capture thread exited.")
        except Exception as e:
            robot_print_error(f"Exception found in video---{e}")

    def robust_power_cycle(self, delay_power_on, delay_power_off, timer, ign_on=None, ign_off=None):
        """
        This method is Robustness test for sleep wakeup.
        :param delay_power_on:delay_wakeup value from Robot script provided by user for delay in msec.
        :param delay_power_off:delay_sleep value from Robot script provided by user for delay in msec.
        :param timer: User can define n number of times and "inf" to run infinity times
        :param ign_on: Default None unless if the user provided Ignition on signal
        :param ign_off: Default None unless if the user provided Ignition on signal
        :return: None
        """
        try:
            self.robust_pps = PpsClass()
            loop = 1
            """Converting msec to sec + 10 ms"""
            delay_x = ((int(delay_power_on) / 1000) + 0.01)
            delay_y = ((int(delay_power_off) / 1000) + 0.01)

            """If user provided inf the loop executes infinity time"""
            if timer != 'inf':
                robot_print_debug(f"int(timer) > loop::{int(timer) > loop}")
                timer = int(timer)

            else:
                timer = float('inf')

            """According on the user-provided timer parameter, the loop runs N times."""
            while timer >= loop:
                robot_print_debug(f"loop count::{loop}")
                self.robust_pps.initialize_pps()

                """The following condition is optional and only applies if the user has provided signal for ignition 
                ON """
                if ign_on is not None:
                    robot_print_debug(f"Ignition ON signal:{ign_on}")
                    self.robust_can.send_can_signal_periodically(ign_on)

                sleep(delay_x)

                """The following condition is optional and only applies if the user has provided signal for ignition 
                OFF """
                if ign_off is not None:
                    robot_print_debug(f"Ignition OFF signal:{ign_off}")
                    task1 = self.robust_can.send_can_signal_periodically(ign_off)
                    self.robust_can.stop_can_periodically_signal(task1)

                self.robust_pps.perform_pps_off()
                sleep(delay_y)
                loop = loop + 1

            self.robust_pps.initialize_pps()
            chk_current_as = self.robust_pps.get_current_value()
            robot_print_debug(f"Checking the current after sleep-:{chk_current_as}")
            if chk_current_as > 0.0:
                robot_print_info("Current verified successfully")
            if ign_on is not None:
                task2 = self.robust_can.send_can_signal_periodically(ign_on)
                sleep(delay_x)
                self.robust_can.stop_can_periodically_signal(task2)

        except Exception as e:
            robot_print_error(f"Error found on the execution:-{e}")
