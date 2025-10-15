import cv2
import os
import time
import sys
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.cVision.cVisionCamera.ConfigurationManager import ConfigurationManager
import time
from datetime import datetime
import openpyxl
from openpyxl import load_workbook
import pandas as pd
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.ImageFinder import ImageFinder
from Robo_FIT.GenericLibraries.GenericOpLibs.cVision.cVisionCamera import cVisionCam
import threading
import ctypes


class cVisionImage:
    def __init__(self):
        """Initializes the cVision class."""
        try:
            self.common_keyword = CommonKeywordsClass()
            self.test_case_name = None
            self.config_manager = ConfigurationManager()
            self.image = ImageFinder()
            self.cVisioncam = cVisionCam.cVisionCam()
            robot_print_info("cVision initialized.")
        except Exception as e:
            robot_print_error(f"Initialization failed: {str(e)}")
            raise
    def read_column_from_excel(self, get_excel_path, sheet_name, column_letter):
        """This function is created to read entire row colmn from an excel sheet .
                parm:
                sheet_name - Sheet to be read
                column_letter - Column to be read
                return : read values
                                        """
        try:
            workbook = openpyxl.load_workbook(get_excel_path)
            sheet = workbook[sheet_name]
            column_values = [cell.value for cell in sheet[column_letter]]
            return column_values
        except Exception as e:
            return str(e)

    def get_image_data_from_excel(self, excel_path):
        """ This function is used to get image data from backend excel """
        List_of_images = self.read_column_from_excel(excel_path, "NewSheet", "A")
        List_of_time = self.read_column_from_excel(excel_path, "Sheet", "G")
        robot_print_info(f"List_of_images == {List_of_images}")
        robot_print_info(f"List_of_time == {List_of_time}")
        return  List_of_images, List_of_time


    def detect_one_image(self, files, template_path, buffer_path, buffer_size, threshold):
        """ This function is used to detect the start and stop of the 1st blink.
        files - List of files in buffer
        template_path - Template path
        buffer_path - buffer path
        buffer_size - buffer size"""

        coordinates = [" "] * len(files)
        detection_flag = 0
        try:
            for i in range(1, int(len(files))):
                img_temp = buffer_path + "\\" + files[i]
                robot_print_info(f"img_temp === {img_temp}")
                robot_print_info(f"template_path === {template_path}")
                robot_print_info(f"threshold === {threshold}")
                coordinates[i] = self.image.is_img_in_img(img_temp, template_path, threshold=float(threshold))
                robot_print_info(f"coordinates[i] {coordinates[i]}")
                if coordinates[i] != []:
                    robot_print_info(f"i in line no 314 {i}")
                    detection_flag = i
                    robot_print_info(f"coordinates type == {type(coordinates)}")
                    return detection_flag, coordinates
            if detection_flag == 0:
                return detection_flag, coordinates
        except Exception as e:
            robot_print_info(f"Exception occured == {e}")

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

    def detect_on_time(self, files, template_path, buffer_path, buffer_size, threshold):
        """ This function is used to detect the start and stop of the 1st blink.
        files - List of files in buffer
        template_path - Template path
        buffer_path - buffer path
        buffer_size - buffer size"""

        coordinates = [" "] * len(files)
        detection_flag = 0
        start_flag = 0
        end_flag = 0
        initial_state = ""
        current_state = ""
        try:
            for i in range(1, int(len(files))):
                robot_print_info(f"Cycle =  : {i}")
                img_temp = buffer_path + "\\" + files[i]
                robot_print_info(f"buffer_path + files[i] : {img_temp}")
                coordinates[i] = self.image.is_img_in_img(img_temp, template_path, threshold=float(threshold))
                robot_print_info(f"coordinates[i] == :{coordinates[i]}")
                if i == 1:
                    robot_print_info(f"i == 1 is true ")
                    if coordinates[i] != []:
                        initial_state = "TT_Detected"
                        robot_print_info(f"initial_state === :{initial_state}")
                        robot_print_error("Image is detected during start of the execution")
                        #raise Exception("Image is detected during start of the execution")
                    else:
                        initial_state = "TT_Not_Detected"
                        robot_print_info(f"initial_state === :{initial_state}")
                robot_print_info(f"coordinates[i] === :{coordinates[i]}")
                if coordinates[i] != []:
                    robot_print_info(f"coordinates[i] != [] is true ")
                    current_state = "TT_Detected"
                else:
                    current_state = "TT_Not_Detected"
                    robot_print_info(f"coordinates[i] != [] is false ")
                if initial_state == "TT_Not_Detected" and end_flag == 0 and coordinates[i] != [] and start_flag == 0:
                    start_flag = i
                    robot_print_info(f"Start flag set successfully === :{start_flag} initial state === {initial_state}")
                if start_flag != 0 and initial_state == current_state:
                    end_flag = i
            robot_print_info(f"return hit ")
            return start_flag, end_flag
        except Exception as e:
            robot_print_info(f"Exception occured == {e}")

    def cVision_check_template_match(self, cvision_path, template_path, time_limit, threshold, save_dir="captured_images", camera=0):
        """ This function is used to detect whether the templete exist in any of the buffer image of not.
                cvision_path - List of files in buffer
                template_path - Template path
                time - time array
                threshold - threshold for patternmatching
                save_dir - image reposidory name in reports"""

        if self.config_manager.get_manual_fps() == "Yes" or self.config_manager.get_manual_fps() == "yes":
            fps = self.config_manager.get_fps()
            robot_print_info(f"Manual FPS taken from JSON === {fps}")
        else:
            fps = self.cVisioncam.get_camera_fps(camera)
            robot_print_info(f"FPS is calculated dynamically")
        buffer_size = time_limit * fps
        robot_print_info(f"buffer_size == {buffer_size}")
        save_dir_image = os.path.join(cvision_path, save_dir)
        excel_path = os.path.join(cvision_path, "cVision_img.xlsx")
        files, time_array = self.get_image_data_from_excel(excel_path)
        coordinates = [" "] * len(files)
        robot_print_info(f"coordinates type 2 == {type(coordinates)}")
        detection_flag, coordinates = self.detect_one_image(files, template_path, save_dir_image, buffer_size, threshold)
        robot_print_info(f"coordinates == {coordinates}")
        robot_print_info(f"line no 367")
        if detection_flag != 0:
            time_of_detection = time_array[int(detection_flag)]
            time_obj = datetime.strptime(time_of_detection, "%H%M%S.%f")
            time_of_detection = time_obj.strftime("%H:%M:%S:%f")
            robot_print_info(f"time_of_detection == :{time_of_detection}")
            robot_print_info(f"Detected in file == :{files[int(detection_flag)]}")
            return files[int(detection_flag)]
        else:
            robot_print_info(f"Image not detected")
            return None

    def cVision_measure_template_match_time(self, cvision_path, template_path, time, threshold, save_dir="captured_images", camera=0):
        """ This function is crated to measure on time of a teltale or a warning
         cvision_path - List of files in buffer
         template_path - Template path
         time - time array
         threshold - threshold for patternmatching
          save_dir - image reposidory name in reports"""
        if self.config_manager.get_manual_fps() == "Yes" or self.config_manager.get_manual_fps() == "yes":
            fps = self.config_manager.get_fps()
            robot_print_info(f"Manual FPS taken from JSON")
        else:
            fps = self.cVisioncam.get_camera_fps(camera)
            robot_print_info(f"FPS is calculated dynamically")
        buffer_size = time * fps
        robot_print_info(f"buffer_size == {buffer_size}")
        save_dir_image = os.path.join(cvision_path, save_dir)
        excel_path = os.path.join(cvision_path, "cVision_img.xlsx")
        files, time_array = self.get_image_data_from_excel(excel_path)
        start_flg, end_flg = self.detect_on_time(files, template_path, save_dir_image, buffer_size, threshold)
        robot_print_info(f"start_flg == :{start_flg} end_flg === {end_flg}")
        robot_print_info(f"time_array[end_flg == :{time_array[end_flg]} time_array[start_flg] === {time_array[start_flg]}")
        time_calc = self.calculate_time_difference(time_array[end_flg], time_array[start_flg])
        robot_print_info(f"time_calc == :{time_calc}")
        return time_calc


    def cVision_measure_pre_template_match_time(self, cvision_path, template_path, time, threshold, save_dir="captured_images", camera=0):
        """ This function is created to measure the time taken to enable a Telltale or Warning
        cvision_path - List of files in buffer
         template_path - Template path
         time - time array
         threshold - threshold for patternmatching
          save_dir - image reposidory name in reports """
        if self.config_manager.get_manual_fps() == "Yes" or self.config_manager.get_manual_fps() == "yes":
            fps = self.config_manager.get_fps()
            robot_print_info(f"Manual FPS taken from JSON")
        else:
            fps = self.cVisioncam.get_camera_fps(camera)
            robot_print_info(f"FPS is calculated dynamically")
        buffer_size = time * fps
        save_dir_image = os.path.join(cvision_path, save_dir)
        excel_path = os.path.join(cvision_path, "cVision_img.xlsx")
        files, time_array = self.get_image_data_from_excel(excel_path)
        coordinates = [" "] * len(files)
        robot_print_info(f"coordinates type 2 == {type(coordinates)}")
        detection_flag, coordinates = self.detect_one_image(files, template_path, save_dir_image, buffer_size, threshold)
        robot_print_info(f"coordinates == {coordinates}")
        if detection_flag != 0:
            time_taken_for_detection = self.calculate_time_difference(time_array[int(detection_flag)], time_array[0])
            robot_print_info(f"time_taken_for_detection == :{time_taken_for_detection}")
            return time_taken_for_detection
        else:
            robot_print_info(f"Image not detected")
            return None

    def get_first_hmi_time(self, folder_path1, template_path, threshold, save_dir1="captured_images"):
        image = ImageFinder()
        folder_path = os.path.join(folder_path1, save_dir1)
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

        # Sort files by extracted timestamp
        image_files.sort(key=self.extract_datetime_from_filename)

        # Get the timestamp of the first image
        first_image_time = self.extract_datetime_from_filename(image_files[0])
        print("++++++++++++++++++++++++++++", first_image_time)

        for image_file in image_files[1:]:
            coordinates = image.is_img_in_img(os.path.join(folder_path, image_file), template_path,
                                              threshold=float(threshold))
            if coordinates:
                matched_image_time = self.extract_datetime_from_filename(image_file)

                # Compute time difference in floating-point seconds
                time_difference = matched_image_time - first_image_time
                print(f"Time difference between {image_files[0]} and {image_file} is {time_difference:.6f} seconds.")
                return time_difference

    def extract_datetime_from_filename(self,filename):
        # Extract timestamp components from the filename
        parts = filename.split('_')
        date_str = parts[1]  # YYYYMMDD
        time_str = parts[2]  # HHMMSS
        microseconds_str = parts[3].split('.')[0]  # Extract only numeric part before .jpg

        # Convert to floating-point seconds for precise subtraction
        timestamp = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        microseconds = int(microseconds_str) / 1_000_000  # Convert to seconds fraction
        return timestamp.timestamp() + microseconds  # Convert datetime to float (UNIX time)

    # def get_first_hmi_time(self, folder_path1, template_path, threshold,save_dir1="captured_images"):
    #     image = ImageFinder()
    #     folder_path = os.path.join(folder_path1, save_dir1)
    #     image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]
    #
    #     # Sort files by extracted timestamp
    #     image_files.sort(key=self.extract_datetime_from_filename)
    #
    #     # Check if there are any image files
    #     if not image_files:
    #         print("No image files found in the specified folder.")
    #         return None
    #
    #     # Get the timestamp of the first image
    #     first_image_time = self.extract_datetime_from_filename(image_files[0])
    #
    #     for image_file in image_files[1:]:
    #         coordinates = image.is_img_in_img(os.path.join(folder_path, image_file), template_path,
    #                                           threshold=float(threshold))
    #         if coordinates:
    #             matched_image_time = self.extract_datetime_from_filename(image_file)
    #
    #             # Compute time difference in floating-point seconds
    #             time_difference = matched_image_time - first_image_time
    #             print(f"Time difference between {image_files[0]} and {image_file} is {time_difference:.6f} seconds.")
    #             return time_difference
    #
    # def extract_datetime_from_filename(self, filename):
    #     # Extract timestamp components from the filename
    #     parts = filename.split('_')
    #
    #     # Check if parts have enough elements
    #     if len(parts) < 4:
    #         print(f"Filename '{filename}' does not have enough parts to extract date and time.")
    #         return None  # or raise an exception
    #
    #     date_str = parts[1]  # YYYYMMDD
    #     time_str = parts[2]  # HHMMSS
    #     microseconds_str = parts[3].split('.')[0]  # Extract only numeric part before .jpg
    #
    #     # Convert to floating-point seconds for precise subtraction
    #     timestamp = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
    #     microseconds = int(microseconds_str) / 1_000_000  # Convert to seconds fraction
    #
    #     return timestamp.timestamp() + microseconds

# if __name__ =='__main__':
#     excel_test_path = "C:\RF_Env\Dhivya\RoboFIT_DI_RE_WC_RawCan_\CRE\SWE5_SWIntegrationTest\Test_Reports\RE_P3F2_OAT_Feb_19_2025_14_46_30\cVision\cVision_Result\TC4\cVision_img.xlsx"
#     h = cVisionImage()
#     h.format_inside_excel(excel_test_path)
