from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Telltale.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Telltale.IvisionClass import IvisionClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Img.IvisionImg import IvisionImg
import requests
import os
from math import sqrt
import re
import pandas as pd


class IvisionTelltale:
    def __init__(self):
        """Initialize with the server URL and load expected colors."""
        self.config_manager = ConfigurationManager()
        self.test_case_name = None
        self.iVision_Img = IvisionImg()
        self.oem = self.config_manager.get_oem()
        ivision_telltale_url = self.config_manager.get_url("detect_telltale")
        ivision_telltale_debug_url = self.config_manager.get_url("detect_telltale_debug")
        self.ivision_telltale = IvisionClass(ivision_telltale_url)
        self.ivision_telltale_debug = IvisionClass(ivision_telltale_debug_url)

        self.excel_file_path = self.config_manager.get_path('excel_file_path')
        self.business_critical_detect_url = self.config_manager.get_url('business_critical_detect')
        self.business_critical_debug_detect_url = self.config_manager.get_url('business_critical_debug_detect')

        self.hmi_overlap_high_threshold = self.config_manager.get_roi_parameters("hmi_overlap_high_threshold")
        self.check_business_critical_area = self.config_manager.get_roi_parameters("check_business_critical_area")
        self.custom_centroids = self.config_manager.get_roi_parameters("custom_centroids")
        self.use_template_matching = self.config_manager.get_roi_parameters("use_template_matching")
        self.advanced_color_detection = self.config_manager.get_roi_parameters("advanced_color_detection")
        self.hmi_overlap_low_threshold = self.config_manager.get_roi_parameters("hmi_overlap_low_threshold")
        self.custom_centroids_type = self.config_manager.get_roi_parameters("custom_centroids_type")
        self.num_expected_colors = self.config_manager.get_roi_parameters("num_expected_colors")


    def __color_distance(self, reference_color, response_color):
        """
        Calculate the Euclidean distance between two RGB colors.

        :param reference_color: The first color in hex format (e.g., '#RRGGBB').
        :param response_color: The second color in hex format (e.g., '#RRGGBB').
        :return: The Euclidean distance between the two colors.
        """
        r1, g1, b1 = int(reference_color[1:3], 16), int(reference_color[3:5], 16), int(reference_color[5:7], 16)
        r2, g2, b2 = int(response_color[1:3], 16), int(response_color[3:5], 16), int(response_color[5:7], 16)
        return sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    def is_color_similar(self, reference_color, response_color, threshold=30):
        """
        Check if two colors are similar within a given threshold.

        :param reference_color: The expected (reference) color in hex format.
        :param response_color: The detected color in hex format.
        :param threshold: The maximum permissible Euclidean distance between the colors.
        :return: True if the colors are similar, else False.
        """
        return self.__color_distance(reference_color, response_color) <= threshold

    def ivision_detect_telltale(self, test_case_name, telltale_name, state="ON"):
        """
        Detect telltale using test case name and telltale name.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param telltale_name: The name of the telltale.
        :param state: The state of the telltale to validate (default is "ON").
        :return: True if the detection matches the expected color, else False.
        """
        try:
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            response = self.ivision_telltale.get_response_server(image_name, oem=self.oem)
            robot_print_info(response)
            detections = response.get('result', {}).get('detections', [])

            expected_color = self.config_manager.get_telltale_state_color(telltale_name, state)

            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('class') == telltale_name:
                        response_color = item.get('color')
                        is_similar = self.is_color_similar(expected_color, response_color)
                        robot_print_info(
                            f"Expected color: {expected_color}, Detected color: {response_color}, Similar: {is_similar}")
                        return is_similar

            return False
        except Exception as e:
            raise RuntimeError(f"Error in iVision_Detect_Telltale: {e}")

    def ivision_telltale_save_model_image(self, test_case_name, telltale_name):
        """
        Debug mode for detecting telltale with test case name.

        :param test_case_name: The test case name used for fetching the image folder path.
        :param telltale_name: The name of the telltale.
        :return: A dictionary with the input image path and detected image path if successful.
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

            # POST request with input image
            with open(input_image_path, 'rb') as image_file:
                response = requests.post(
                    self.ivision_telltale_debug.url,
                    files={'image': image_file},
                    data={'oem': self.oem}
                )
                response.raise_for_status()

            if response.headers['content-type'] == 'image/png':
                result_image_dir = self.iVision_Img.get_ivision_result_path()
                detected_image_path = os.path.join(result_image_dir, f"{telltale_name}_detected_image.png")

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

    def ivision_detect_telltale_and_save_model_image(self, test_case_name, telltale_name, state="ON"):
        """
        Detect telltale using test case name , telltale name and the telltale color.

        :param test_case_name: The test case name (used for fetching image folder path).
        :param telltale_name: The name of the telltale to detect.
        :param state: The state of the telltale to validate (default is "ON").
        :return: True if the detection matches the expected color, else False.
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            self.ivision_telltale_save_model_image(test_case_name, telltale_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            # Get the response server
            response = self.ivision_telltale.get_response_server(image_name, oem=self.oem)
            robot_print_info("response", response)
            detections = response.get('result', {}).get('detections', [])

            expected_color = self.config_manager.get_telltale_state_color(telltale_name, state)

            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('class') == telltale_name:
                        response_color = item.get('color')
                        is_similar = self.is_color_similar(expected_color, response_color)
                        robot_print_info(
                            f"Expected color: {expected_color}, Detected color: {response_color}, Similar: {is_similar}")
                        return is_similar
            return False
        except Exception as e:
            raise RuntimeError(f"Error in ivision_detect_telltale_debug_image: {e}")

    def ivision_detect_tellatale_debug(self, test_case_name, telltalename, state="ON"):
        """
        Detect telltale using test case name and telltale name.

        :param test_case_name: The test case name (used for fetching image folder path).
        :param telltalename: The name of the telltale to detect.
        :param state: The state of the telltale to validate (default is "ON").
        :return: True if the detection matches the expected color, else False.
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            self.ivision_telltale_save_model_image(test_case_name, telltalename)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            # Get the response server
            response = self.ivision_telltale.get_response_server(image_name, oem=self.oem)
            robot_print_info("response", response)
            detections = response.get('result', {}).get('detections', [])


            expected_color = self.config_manager.get_telltale_state_color(telltalename, state)

            for detection in detections:
                for item in detection.get('detection', []):
                    if item.get('class') == telltalename and item.get('color') == expected_color:
                        return True
            return False
        except Exception as e:
            raise RuntimeError(f"Error in ivision_detect_telltale_debug_image: {e}")

    def ivision_detect_all_telltale(self, imag_name, telltale_list):
        """Detect multiple telltales from a list in a single image."""
        try:
            results = []
            for telltale in telltale_list:
                response = self.ivision_telltale.get_response_server(imag_name, oem=self.oem)
                if telltale in response:
                    results.append({telltale: "Found"})
                else:
                    results.append({telltale: "Not Found"})
            return results
        except Exception as e:
            raise RuntimeError(f"Error in iVision_Detect_All_Telltale: {e}")

    def ivision_auto_detect_telltale(self, test_case_name, object_names):
        """
        Detect telltales using object names from Excel and validate their colors.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param object_names: List of object names to detect.
        :return: Dictionary of expected object names with True/False based on color match.
        """
        try:
            if isinstance(object_names, str):
                object_names = eval(object_names)

            if len(object_names) > 10:
                raise ValueError("You can only pass up to 10 object names.")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()
            robot_print_info(f'Input image taken from: {image_path}')

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            results = {}

            # Get detections once
            response_json = self.ivision_telltale.get_response_server(image_name, oem=self.oem)
            detections = response_json.get('result', {}).get('detections', [])

            # Upload image once
            with open(image_name, 'rb') as image_file:
                response = requests.post(
                    self.ivision_telltale_debug.url,
                    files={'image': image_file},
                    data={'oem': self.oem}
                )
                if 'image/png' in response.headers.get('content-type', ''):
                    result_image_dir = self.iVision_Img.get_ivision_result_path()
                    detected_image_path = os.path.join(result_image_dir, "ivision_auto_detect_telltale_detected_image.png")
                    with open(detected_image_path, 'wb') as detected_file:
                        detected_file.write(response.content)
                    robot_print_info(f"Detected image saved at: {detected_image_path}")

            for object_name in object_names:
                try:
                    row = df[df.iloc[:, 3] == object_name]
                    if row.empty:
                        robot_print_info(f"Object name '{object_name}' not found in Excel.")
                        results[object_name] = False
                        continue

                    expected_object_name = row.iloc[0, 4]
                    expected_color = row.iloc[0, 5]

                    match_found = False
                    detected_color = None
                    for detection in detections:
                        for item in detection.get('detection', []):
                            if item.get('class') == expected_object_name:
                                detected_color = item.get('color')
                                is_similar = self.is_color_similar(expected_color, detected_color)
                                robot_print_info(
                                    f"{expected_object_name}: Expected: {expected_color}, Detected: {detected_color}, Match: {is_similar}")
                                match_found = is_similar
                                break
                        if match_found:
                            break

                    results[expected_object_name, detected_color] = match_found

                except Exception as obj_err:
                    robot_print_info(f"Error processing object '{object_name}': {obj_err}")
                    results[object_name] = False

            all_match = all(results.values())
            if not all_match:
                raise AssertionError(f"Telltale color mismatch: {results}")
            return True,results

        except Exception as e:
            raise RuntimeError(f"Error in ivision_auto_detect_telltales: {e}")

    def get_response_server(self, image_path, region, filter_threshold=90, oem="GM", save_image_path=None, **kwargs):
        """Send a POST request to the server with the provided image and parameters, and handle the response."""
        headers = {
            'accept': 'application/json' if 'business_critical_detect' in self.business_critical_detect_url else 'image/*'}
        data = {
            'filter_threshold': str(filter_threshold),
            'oem': self.oem,
            'region': region
        }
        data.update(kwargs)

        file_extension = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg' if file_extension in ['.jpg', '.jpeg'] else 'image/png'
        files = {'image': (os.path.basename(image_path), open(image_path, 'rb'), mime_type)}

        try:
            response = requests.post(self.url, headers=headers, data=data, files=files)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type')

            if 'application/json' in content_type:
                json_response = response.json()
                robot_print_info(f'JSON response: {json_response}')
                return json_response
            elif 'image/' in content_type:
                if save_image_path:
                    with open(save_image_path, 'wb') as f:
                        f.write(response.content)
                    robot_print_info(f"Image saved to {save_image_path}")
                    return f"Image saved to {save_image_path}"
                else:
                    return response.content
            else:
                return response.text
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e.filename}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while sending the request: {e}")

    def ivision_detect_telltale_with_roi_debug(self, test_case_name, ROI):
        """
            Debug detection of a telltale's color within a specified region of interest in the image, saving annotated results.

            :param test_case_name: The test case name for fetching images.
            :param ROI: The region of interest in the format "x_min y_min width height".
            :return: List with a dictionary mapping the ROI string to the detected color.
            :returns: False if an error occurs during the process.
        """
        try:
            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()
            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            roi_coords = list(map(int, ROI.split()))
            x_min, y_min, width, height = roi_coords

            x_max = x_min + width
            y_max = y_min + height

            reformatted_roi = f"{x_min} {y_min} {x_max} {y_max}"
            robot_print_info(f'Reformatted ROI: {reformatted_roi}')

            self.url = self.business_critical_detect_url
            response = self.get_response_server(
                image_name,
                region=reformatted_roi,
                hmi_overlap_high_threshold=self.hmi_overlap_high_threshold,
                check_business_critical_area=self.check_business_critical_area,
                custom_centroids=self.custom_centroids,
                use_template_matching=self.use_template_matching,
                advanced_color_detection=self.advanced_color_detection,
                hmi_overlap_low_threshold=self.hmi_overlap_low_threshold,
                custom_centroids_type=self.custom_centroids_type,
                num_expected_colors=self.num_expected_colors
            )
            response_image_path = os.path.join(self.iVision_Img.get_ivision_result_path(),
                                               f'detect_telltale_with_roi_debug_{ROI}.png')
            self.url = self.business_critical_debug_detect_url
            self.get_response_server(
                image_name, region=reformatted_roi, save_image_path=response_image_path,
            )
            robot_print_info(f'{response_image_path}')

            detected_class = response['result']['detections'][0]['detection'][0]['class']
            detected_color = response['result']['detections'][0]['detection'][0]['color']
            robot_print_info(f"Detected class: {detected_class}:{detected_color}")

            return detected_class, detected_color

        except Exception as e:
            robot_print_error(f"Error in ivision_detect_telltale_with_ROI: {e}")
            return False

    def ivision_auto_detect_telltale_with_roi(self, test_case_name, object_names):
        """
        Detect telltale objects within defined regions of interest and compare the detected class to the expected class from Excel.

        :param test_case_name: The name of the test case folder used to fetch images.
        :param object_names: The list of object names (or a string convertible to a list) to detect; up to 10 objects supported.
        :return: True if all detected classes match expected classes, otherwise False.
        """
        try:
            if isinstance(object_names, str):
                object_names = eval(object_names)

            if len(object_names) > 10:
                raise ValueError("You can only pass up to 10 object names.")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()
            robot_print_info(f'Input image taken from : {image_path}')
            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            second_row = df.iloc[1]
            roi_col = second_row['Unnamed: 1']

            results = []

            for object_name in object_names:
                try:
                    row = df[df.iloc[:, 3] == object_name]
                    if row.empty:
                        robot_print_info(f"Object name '{object_name}' not found in the Excel sheet.")
                        results.append({object_name: False})
                        continue

                    roi = row.iloc[0, 1]
                    roi_str = str(roi)
                    if ',' in roi_str:
                        formatted_roi = ' '.join([x.strip() for x in roi_str.split(',')])
                    else:
                        groups = re.findall(r'\d{1,4}', roi_str)
                        formatted_roi = " ".join(groups)
                    robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')

                    roi_coords = list(map(int, formatted_roi.split()))
                    x_min, y_min, width, height = roi_coords
                    x_max = x_min + width
                    y_max = y_min + height
                    reformatted_roi = f"{x_min} {y_min} {x_max} {y_max}"
                    robot_print_info(f'Reformatted ROI: {reformatted_roi}')

                    self.url = self.business_critical_detect_url
                    response = self.get_response_server(
                        image_name,
                        region=reformatted_roi,
                        hmi_overlap_high_threshold=self.hmi_overlap_high_threshold,
                        check_business_critical_area=self.check_business_critical_area,
                        custom_centroids=self.custom_centroids,
                        use_template_matching=self.use_template_matching,
                        advanced_color_detection=self.advanced_color_detection,
                        hmi_overlap_low_threshold=self.hmi_overlap_low_threshold,
                        custom_centroids_type=self.custom_centroids_type,
                        num_expected_colors=self.num_expected_colors
                    )

                    response_image_path = os.path.join(self.iVision_Img.get_ivision_result_path(),
                                                       f'auto_detect_telltale_with_roi_{object_name}.png')
                    self.url = self.business_critical_debug_detect_url
                    self.get_response_server(
                        image_name, region=reformatted_roi, save_image_path=response_image_path,
                    )
                    robot_print_info(f'{response_image_path}')

                    detected_class = response['result']['detections'][0]['detection'][0]['class']
                    expected_class = row.iloc[0, 4]
                    match = detected_class == expected_class
                    robot_print_info(
                        f"{object_name}: Expected: {expected_class}, Detected: {detected_class}, Match: {match}")
                    results.append({object_name: match})

                except Exception as obj_err:
                    robot_print_info(f"Error processing object '{object_name}': {obj_err}")
                    results.append({object_name: False})

            all_match = all(list(result.values())[0] for result in results)

            for result in results:
                for object_name, response in result.items():
                    robot_print_info(f"{object_name}: {response}")

            return all_match,results

        except Exception as e:
            robot_print_error(f"Error in ivision_auto_detect_telltale_with_roi: {e}")
            return False

    def ivision_auto_detect_telltale_with_roi_debug(self, test_case_name, object_names):
        """
            Detect telltale objects within defined regions of interest, show the detected color for each, and save annotated images for debugging.

            :param test_case_name: The name of the test case folder used to fetch images.
            :param object_names: The list of object names (or a string convertible to a list) to detect; up to 10 objects supported.
            :return: List of dictionaries containing the detected color for each object name.
            :returns: False if an error occurs during the process.
        """
        try:
            if isinstance(object_names, str):
                object_names = eval(object_names)

            if len(object_names) > 10:
                raise ValueError("You can only pass up to 10 object names.")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()
            robot_print_info(f'Input image taken from : {image_path}')
            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            second_row = df.iloc[1]
            roi_col = second_row['Unnamed: 1']

            df = pd.read_excel(self.excel_file_path, engine='openpyxl', dtype={roi_col: str})

            results = []
            for object_name in object_names:
                try:
                    row = df[df.iloc[:, 3] == object_name]
                    if row.empty:
                        robot_print_info(f"Object name '{object_name}' not found in the Excel sheet.")
                        results.append({object_name: None})
                        continue

                    roi = row.iloc[0, 1]
                    roi_str = str(roi)
                    if ',' in roi_str:
                        formatted_roi = ' '.join([x.strip() for x in roi_str.split(',')])
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')
                    else:
                        groups = re.findall(r'\d{1,4}', roi_str)
                        formatted_roi = " ".join(groups)
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')

                    roi_coords = list(map(int, formatted_roi.split()))
                    x_min, y_min, width, height = roi_coords
                    x_max = x_min + width
                    y_max = y_min + height
                    reformatted_roi = f"{x_min} {y_min} {x_max} {y_max}"
                    robot_print_info(f'Reformatted ROI: {reformatted_roi}')

                    self.url = self.business_critical_detect_url
                    response = self.get_response_server(
                        image_name,
                        region=reformatted_roi,
                        hmi_overlap_high_threshold=self.hmi_overlap_high_threshold,
                        check_business_critical_area=self.check_business_critical_area,
                        custom_centroids=self.custom_centroids,
                        use_template_matching=self.use_template_matching,
                        advanced_color_detection=self.advanced_color_detection,
                        hmi_overlap_low_threshold=self.hmi_overlap_low_threshold,
                        custom_centroids_type=self.custom_centroids_type,
                        num_expected_colors=self.num_expected_colors
                    )

                    response_image_path = os.path.join(self.iVision_Img.get_ivision_result_path(),
                                                       f'auto_detect_telltale_with_roi_debug_{object_name}.png')
                    self.url = self.business_critical_debug_detect_url
                    self.get_response_server(
                        image_name, region=reformatted_roi, save_image_path=response_image_path,
                    )
                    robot_print_info(f'{response_image_path}')

                    detected_color = response['result']['detections'][0]['detection'][0]['color']
                    results.append({object_name: detected_color})

                except Exception as obj_err:
                    robot_print_info(f"Error processing object '{object_name}': {obj_err}")
                    results.append({object_name: None})

            for result in results:
                for object_name, response in result.items():
                    robot_print_info(f"{object_name}: {response}")

            return results

        except Exception as e:
            robot_print_error(f"Error in ivision_auto_detect_telltale: {e}")
            return False

    def ivision_auto_detect_telltale_color_with_roi(self, test_case_name, object_names):
        """
        Detect telltale objects using their name and expected color (from Excel), compare with detected color, and check for color similarity.

        :param test_case_name: The test case name for fetching image folder path.
        :param object_names: The list of object names (or string convertible to a list) to detect; up to 10 supported.
        :return: True if all detected colors are similar to expected colors, otherwise False.
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            if isinstance(object_names, str):
                object_names = eval(object_names)

            if len(object_names) > 10:
                raise ValueError("You can only pass up to 10 object names.")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            second_row = df.iloc[1]
            roi_col = second_row['Unnamed: 1']

            df = pd.read_excel(self.excel_file_path, engine='openpyxl', dtype={roi_col: str})

            results = []
            for object_name in object_names:
                try:
                    row = df[df.iloc[:, 3] == object_name]
                    if row.empty:
                        robot_print_info(f"Object name '{object_name}' not found in the Excel sheet.")
                        results.append({object_name: False})
                        continue

                    roi = row.iloc[0, 1]
                    roi_str = str(roi)
                    if ',' in roi_str:
                        formatted_roi = ' '.join([x.strip() for x in roi_str.split(',')])
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')
                    else:
                        groups = re.findall(r'\d{1,4}', roi_str)
                        formatted_roi = " ".join(groups)
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')

                    roi_coords = list(map(int, formatted_roi.split()))
                    x_min, y_min, width, height = roi_coords
                    x_max = x_min + width
                    y_max = y_min + height
                    reformatted_roi = f"{x_min} {y_min} {x_max} {y_max}"
                    robot_print_info(f'Reformatted ROI: {reformatted_roi}')

                    self.url = self.business_critical_detect_url
                    response = self.get_response_server(
                        image_name,
                        region=reformatted_roi,
                        hmi_overlap_high_threshold=self.hmi_overlap_high_threshold,
                        check_business_critical_area=self.check_business_critical_area,
                        custom_centroids=self.custom_centroids,
                        use_template_matching=self.use_template_matching,
                        advanced_color_detection=self.advanced_color_detection,
                        hmi_overlap_low_threshold=self.hmi_overlap_low_threshold,
                        custom_centroids_type=self.custom_centroids_type,
                        num_expected_colors=self.num_expected_colors
                    )

                    response_image_path = os.path.join(self.iVision_Img.get_ivision_result_path(),
                                                       f'auto_detect_telltale_color_with_roi_{object_name}.png')
                    self.url = self.business_critical_debug_detect_url
                    self.get_response_server(
                        image_name, region=reformatted_roi, save_image_path=response_image_path,
                    )
                    robot_print_info(f'{response_image_path}')

                    expected_color = row.iloc[0, 5]
                    detected_color = response['result']['detections'][0]['detection'][0]['color']

                    is_similar = self.is_color_similar(expected_color, detected_color)
                    robot_print_info(
                        f"Expected color: {expected_color}, Detected color: {detected_color}, Similar: {is_similar}")
                    results.append({object_name: is_similar})

                except Exception as obj_err:
                    robot_print_info(f"Error processing object '{object_name}': {obj_err}")
                    results.append({object_name: False})

            all_match = all(list(result.values())[0] for result in results)

            for result in results:
                for object_name, response in result.items():
                    robot_print_info(f"{object_name}: {response}")

            return all_match,results

        except Exception as e:
            raise RuntimeError(f"Error in ivision_auto_detect_telltale_color: {e}")

    def ivision_detect_telltale_color_with_roi(self, test_case_name, object_names, colors):
        """
        Detect telltale objects with both object names and expected colors as input arguments; compare with detected color for similarity.

        :param test_case_name: The test case name (used for fetching image folder path).
        :param object_names: The list of object names to detect.
        :param colors: The list of expected colors, matching the length of object_names.
        :return: True if all detected colors are similar to expected colors, otherwise False.
        :raises RuntimeError: If an error occurs during the process.
        """
        try:
            if isinstance(object_names, str):
                object_names = eval(object_names)
            if isinstance(colors, str):
                colors = eval(colors)

            if len(object_names) > 10:
                raise ValueError("You can only pass up to 10 object names.")
            if len(object_names) != len(colors):
                raise ValueError("The number of object names must match the number of colors.")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")
            input_image = input_images[0]
            image_name = os.path.join(image_path, input_image)

            df = pd.read_excel(self.excel_file_path, engine='openpyxl')
            second_row = df.iloc[1]
            roi_col = second_row['Unnamed: 1']
            df = pd.read_excel(self.excel_file_path, engine='openpyxl', dtype={roi_col: str})

            results = []
            for object_name, expected_color in zip(object_names, colors):
                try:
                    row = df[df.iloc[:, 3] == object_name]
                    if row.empty:
                        robot_print_info(f"Object name '{object_name}' not found in the Excel sheet.")
                        results.append({object_name: False})
                        continue

                    roi = row.iloc[0, 1]
                    roi_str = str(roi)
                    if ',' in roi_str:
                        formatted_roi = ' '.join([x.strip() for x in roi_str.split(',')])
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')
                    else:
                        groups = re.findall(r'\d{1,4}', roi_str)
                        formatted_roi = " ".join(groups)
                        robot_print_info(f'ROI taken from HMI sheet : {formatted_roi}')

                    roi_coords = list(map(int, formatted_roi.split()))
                    x_min, y_min, width, height = roi_coords
                    x_max = x_min + width
                    y_max = y_min + height
                    reformatted_roi = f"{x_min} {y_min} {x_max} {y_max}"
                    robot_print_info(f'Reformatted ROI: {reformatted_roi}')

                    self.url = self.business_critical_detect_url
                    response = self.get_response_server(
                        image_name,
                        region=reformatted_roi,
                        hmi_overlap_high_threshold=self.hmi_overlap_high_threshold,
                        check_business_critical_area=self.check_business_critical_area,
                        custom_centroids=self.custom_centroids,
                        use_template_matching=self.use_template_matching,
                        advanced_color_detection=self.advanced_color_detection,
                        hmi_overlap_low_threshold=self.hmi_overlap_low_threshold,
                        custom_centroids_type=self.custom_centroids_type,
                        num_expected_colors=self.num_expected_colors
                    )

                    response_image_path = os.path.join(self.iVision_Img.get_ivision_result_path(),
                                                       f'detect_telltale_color_with_roi_{object_name}.png')
                    self.url = self.business_critical_debug_detect_url
                    self.get_response_server(
                        image_name, region=reformatted_roi, save_image_path=response_image_path,
                    )
                    robot_print_info(f'{response_image_path}')

                    detected_color = response['result']['detections'][0]['detection'][0]['color']
                    is_similar = self.is_color_similar(expected_color, detected_color)
                    robot_print_info(
                        f"Expected color: {expected_color}, Detected color: {detected_color}, Similar: {is_similar}")
                    results.append({object_name: is_similar})

                except Exception as obj_err:
                    robot_print_info(f"Error processing object '{object_name}': {obj_err}")
                    results.append({object_name: False})

            all_match = all(list(result.values())[0] for result in results)

            for result in results:
                for object_name, response in result.items():
                    robot_print_info(f"{object_name}: {response}")

            return all_match,results

        except Exception as e:
            raise RuntimeError(f"Error in ivision_detect_telltale_color_with_roi: {e}")