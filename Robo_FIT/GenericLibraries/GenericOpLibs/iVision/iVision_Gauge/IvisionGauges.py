from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Gauge.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Gauge.IvisionClass import IvisionClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Img.IvisionImg import IvisionImg
import requests
import os

class  IvisionGauges:
    def __init__(self):
        """Initialize with the server URL and load expected colors."""
        self.config_manager = ConfigurationManager()
        self.test_case_name = None
        self.oem = self.config_manager.get_oem()
        self.iVision_Img = IvisionImg()
        self.ivision_gauges_url = self.config_manager.get_url("detect_gauges_generalised")
        self.ivision_gauges_debug_url = self.config_manager.get_url("detect_gauges_generalised_debug")
        self.ivision_gauges = IvisionClass(self.ivision_gauges_url)
        self.ivision_gauges_debug = IvisionClass(self.ivision_gauges_debug_url)

    def ivision_gauge_get_angle(self, test_case_name, gauge_type: str) -> float:
        """
        Return the angle_deg if the detection matches the specified conditions.
        
        :param test_case_name: The test case name (used for fetching the image folder path).
        :param gauge_type: The type of gauge to detect.
        :return: The angle (in degrees) of the gauge if conditions are met; else returns "Gauge not found".
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            expected_shape = self.config_manager.get_gauge_shape(gauge_type)
            expected_min_value = str(self.config_manager.get_min_value(gauge_type))
            expected_max_value = str(self.config_manager.get_max_value(gauge_type))
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)
            response = self.ivision_gauges.get_response_server(image_name, oem=self.oem)
            robot_print_info(response)
            detections = response.get('result', {}).get('detections', [])
            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('gauge_type') != gauge_type:
                        continue
                    if (item.get('gauge_shape') == expected_shape and
                            item.get('val_scale_max') == expected_max_value and
                            item.get('val_scale_min') == expected_min_value):
                        return item.get('angle_deg')
            return "Gauge not found"
        except Exception as e:
            print(f"Error in check_angle_deg: {e}")
            raise RuntimeError(f"Error in check_angle_deg: {e}")

    def ivision_gauge_get_needlevalue(self, test_case_name, gauge_type: str) -> float:
        """
        Return the value if the detection matches the specified conditions.

        :param test_case_name: The test case name (used for fetching the image folder path).
        :param gauge_type: The type of gauge to detect.
        :return: The needle value of the gauge if conditions are met; else returns "Gauge not found".
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            expected_shape = self.config_manager.get_gauge_shape(gauge_type)
            expected_min_value = str(self.config_manager.get_min_value(gauge_type))
            expected_max_value = str(self.config_manager.get_max_value(gauge_type))
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            response = self.ivision_gauges.get_response_server(image_name, oem=self.oem)
            robot_print_info(response)
            detections = response.get('result', {}).get('detections', [])
            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('gauge_type') != gauge_type:
                        continue
                    if (item.get('gauge_shape') == expected_shape and
                            item.get('val_scale_max') == expected_max_value and
                            item.get('val_scale_min') == expected_min_value):
                        return item.get('value')
            return "Gauge not found"
        except Exception as e:
            print(f"Error in check_value: {e}")
            raise RuntimeError(f"Error in check_value: {e}")

    def iVision_gauge_debug(self, test_case_name, gauge_type):
        """
        Debug mode for detecting a gauge with an image and saving the image.

        :param test_case_name: The test case name used for fetching the image folder path.
        :param gauge_type: The type of gauge to debug.
        :return: A dictionary containing paths for input and detected images, or raises an exception if errors occur.
        :raises RuntimeError: If an error occurs during the process.
        """

        try:
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()


            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            input_image_path = os.path.join(image_path, input_image)


            with open(input_image_path, 'rb') as image_file:
                response = requests.post(
                    self.ivision_gauges_debug_url,
                    files={'image': image_file},
                    data={'oem': self.oem}
                )
                response.raise_for_status()

            if response.headers['content-type'] == 'image/png':
                result_image_dir = self.iVision_Img.get_ivision_result_path()
                detected_image_path = os.path.join(result_image_dir, f"{gauge_type}_detected_image.png")

                with open(detected_image_path, 'wb') as detected_file:
                    detected_file.write(response.content)

                robot_print_info(f"Detected image saved at: {detected_image_path}")
                return {"message": "Images saved successfully", "input_image_path": input_image_path,
                        "detected_image_path": detected_image_path}
            else:
                raise ValueError("Response does not contain a PNG image.")
        except Exception as e:
            robot_print_error(f"Encountered an error in iVision_Telltale_Debug: {e}")
            raise RuntimeError(f"Error in iVision_Telltale_Debug: {e}")

    def ivision_gauge_get_percentage(self, test_case_name, gauge_type: str) -> float:
        """
        Return the percentage if the detection matches the specified conditions.

        :param test_case_name: The test case name (used for fetching the image folder path).
        :param gauge_type: The type of gauge to detect.
        :return: The percentage value of the gauge if conditions are met; else returns "Gauge not found".
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            expected_shape = self.config_manager.get_gauge_shape(gauge_type)
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            response = self.ivision_gauges.get_response_server(image_name, oem=self.oem)
            robot_print_info(response)
            detections = response.get('result', {}).get('detections', [])
            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('gauge_type') != gauge_type:
                        continue
                    if item.get('gauge_shape') == expected_shape:
                        return item.get('percentage')
            return "Gauge not found"
        except Exception as e:
            print(f"Error in check_percentage: {e}")
            raise RuntimeError(f"Error in check_percentage: {e}")