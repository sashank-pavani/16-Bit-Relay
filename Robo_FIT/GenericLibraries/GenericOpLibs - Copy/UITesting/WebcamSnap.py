import os
import sys
import cv2
import time
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug


class WebcamSnap:
    """
    This class is for Capturing Image by External Web camera
    """

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()

    def camera0(self, filename: str, max_attempts=5):
        """
        This method captures the Image from an external web camera and returns the path of the saved screenshot Image.
        :param filename: The filename to save the screenshot image.
        :param max_attempts: Maximum number of attempts to capture a non-blank frame.
        :return: The path of the saved image.
        """
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            robot_print_info("Error: Camera not accessible or not connected.")

        else:
            robot_print_info("Camera is accessible and connected.")

        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
        # cap.set(cv2.CAP_PROP_AUTOFOCUS,0)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        #
        # # Set frame rate (for example, 30 frames per second)
        # cap.set(cv2.CAP_PROP_FPS, 18)
        time.sleep(0.2)

        attempts = 0
        while attempts < max_attempts:
            ret, frame = cap.read()
            if ret and not self.is_blank(frame):
                break
            attempts += 1

        # if not ret or self.is_blank(frame):
        #     robot_print_error("Error with the camera")
        #     cap.release()
        #     cv2.destroyAllWindows()
        #     return None

        Pname = os.path.basename(sys.argv[0])[0:4]
        robot_print_info(f"Pname: {Pname}")
        filename = filename + ".jpg"
        file_name = os.path.join(self.common_keyword.get_image_screenshot_path(), filename)
        robot_print_info(f"file_name:{file_name}")

        cv2.imwrite(file_name, frame)
        time.sleep(1)
        robot_print_info("Screenshot done!")

        cap.release()
        cv2.destroyAllWindows()
        robot_print_info(f"Camera Image Saved in the path: {file_name}")
        return file_name

    def is_blank(self, frame, threshold=30):
        """
        Check if a frame is blank.
        :param frame: Frame to check.
        :param threshold: Threshold for average pixel intensity.
        :return: True if the frame is blank, False otherwise.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_intensity = cv2.mean(gray_frame)[0]
        return avg_intensity < threshold
