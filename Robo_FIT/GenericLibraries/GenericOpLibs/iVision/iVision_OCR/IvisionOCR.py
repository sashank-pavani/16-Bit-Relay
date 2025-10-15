from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_Img.IvisionImg import IvisionImg
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_OCR.IvisionClass import IvisionClass
from Robo_FIT.GenericLibraries.GenericOpLibs.iVision.iVision_OCR.ConfigurationManager import ConfigurationManager
import re
import os

class IvisionOCR:
    def __init__(self):
        """Initialize the IvisionOCR with a ConfigurationManager."""
        self.config_manager = ConfigurationManager()
        self.test_case_name = None
        self.iVision_Img = IvisionImg()

        self.url = self.config_manager.get_url("detect_text")
        self.debug_url = self.config_manager.get_url("detect_text_debug")
        self.iVision_detect_url = IvisionClass(self.url)
        self.iVision_debug_url = IvisionClass(self.debug_url)
        self.detections = self.config_manager.get_detections()

        try:
            self.bw_threshold = self.config_manager.get_ocr_parameters("bw_threshold")
            self.ocr_output = self.config_manager.get_ocr_parameters("ocr_output")
            self.preprocessing_algorithm = self.config_manager.get_ocr_parameters("preprocessing_algorithm")
            self.psm = self.config_manager.get_ocr_parameters("psm")
            self.region = self.config_manager.get_ocr_parameters("region")
            self.confidence_threshold = self.config_manager.get_ocr_parameters("confidence_threshold")
            self.oem = self.config_manager.get_oem()
            self.confidence = self.config_manager.get_confidence()
        except KeyError as e:
            raise ValueError(f"Missing required key in OCRParameters JSON: {e}")

        robot_print_info(f"OCR URL: {self.url}")
        robot_print_info(f"OCR Debug URL: {self.debug_url}")

        self.interword_spaces = None
        self.lang = None

    def ocr_detect_text(self, test_case_name, text_name, interword_spaces=None, lang=None):
        """
        Detect text using the test case name and specified parameters.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param text_name: Name of the text to detect.
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A dictionary with the detection response and verification result.
        """
        try:
            # Use defaults if parameters are not provided by the user
            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"

            self.interword_spaces = interword_spaces
            self.lang = lang
            robot_print_info(f"lang{lang}")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            file_path = os.path.join(image_path, input_image)

            try:
                expected_box = next((item['box'] for item in self.detections if item['text'] == text_name), None)
                if expected_box is None:
                    raise ValueError(f"Text '{text_name}' not found in detections.")
            except (StopIteration, KeyError) as e:
                error_message = (
                    f"Error finding text '{text_name}' in detections. "
                    "Please ensure you have provided the correct text and its Region of Interest (ROI) in the OCR configuration file. "
                    "Verify that the text name matches exactly ."
                )
                robot_print_error(error_message)
                raise ValueError(error_message) from e

            response = self.iVision_detect_url.send_request(
                url=self.url,
                file_path=file_path,
                bw_threshold=self.bw_threshold,
                ocr_output=self.ocr_output,
                interword_spaces=interword_spaces,
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=lang,
                region=self.region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            ).json()

            verification_result = self._verify_response(response, expected_box, text_name)
            robot_print_info(f"Response: {response}")

            return verification_result

        except KeyError as ke:
            robot_print_error(f"Missing required key in response: {ke}")
            raise ValueError(f"Missing required key in response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in detect_text: {e}")
            raise RuntimeError(f"Error in detect_text: {e}")

    def ocr_detect_text_debug(self, test_case_name, text_name):
        """
        Debug text detection using the test case name and save the input and output images.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param text_name: Name of the text to detect (used for file naming).
        :return: A dictionary with the input image path and detected image path if successful.
        """
        try:

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            input_image_path = os.path.join(image_path, input_image)

            response = self.iVision_debug_url.send_request(
                url=self.debug_url,
                file_path=input_image_path,
                bw_threshold=self.bw_threshold,
                ocr_output=self.ocr_output,
                interword_spaces=str(self.interword_spaces),
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=str(self.lang),
                region=self.region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            )

            response_content_type = response.headers.get("content-type")
            robot_print_info(f"Response Content-Type: {response_content_type}")

            if response_content_type == "image/png":

                result_image_dir = self.iVision_Img.get_ivision_result_path()
                detected_image_path = os.path.join(result_image_dir, f"{text_name}_detected_image.png")

                with open(detected_image_path, "wb") as detected_file:
                    detected_file.write(response.content)

                robot_print_info(f"Detected image saved at: {detected_image_path}")
                return {
                    "message": "Images saved successfully",
                    "input_image_path": input_image_path,
                    "detected_image_path": detected_image_path
                }

            else:
                raise ValueError(f"Unexpected response content type: {response_content_type}")

        except KeyError as ke:
            robot_print_error(f"A required key is missing in the request or response: {ke}")
            raise ValueError(f"A required key is missing in the request or response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in detect_text_debug: {e}")
            raise RuntimeError(f"Error in detect_text_debug: {e}")

    def ocr_detect_text_and_debug(self, test_case_name, text_name, interword_spaces=None, lang=None):
        """
        Perform both text detection and debugging in a single operation.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param text_name: Name of the text to detect and debug.
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A dictionary containing both detection and debug results.
        """
        try:
            robot_print_info(f"Starting text detection for text: {text_name}")
            detection_result = self.ocr_detect_text(test_case_name, text_name, interword_spaces, lang)
            robot_print_info(f"Text detection result: {detection_result}")

            robot_print_info(f"Starting debug operation for text: {text_name}")
            debug_result = self.ocr_detect_text_debug(test_case_name, text_name)
            robot_print_info(f"Debugging result: {debug_result}")

            return {
                "detection_result": detection_result,
                "debug_result": debug_result
            }

        except KeyError as ke:
            robot_print_error(f"Missing required key: {ke}")
            raise ValueError(f"Missing required key: {ke}")
        except FileNotFoundError as fnfe:
            robot_print_error(f"File not found: {fnfe}")
            raise FileNotFoundError(f"File not found: {fnfe}")
        except Exception as e:
            robot_print_error(f"Error in detect_text_and_debug: {e}")
            raise RuntimeError(f"Error in detect_text_and_debug: {e}")

    def ocr_search(self, test_case_name, search_word, interword_spaces=None, lang=None):
        """
        Search for a word in the OCR detections and return a list of words matching the letters from the JSON data.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param search_word: The word to search for.
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A list of words matching the letters from the JSON data.
        """
        try:

            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"

            self.interword_spaces = interword_spaces
            self.lang = lang

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            file_path = os.path.join(image_path, input_image)

            response = self.iVision_detect_url.send_request(
                url=self.url,
                file_path=file_path,
                bw_threshold=self.bw_threshold,
                ocr_output=self.ocr_output,
                interword_spaces=interword_spaces,
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=lang,
                region=self.region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            ).json()

            detections = response.get('result', {}).get('detections', [])
            matching_words = []

            for detection in detections:
                for item in detection.get('detection', []):
                    text = item.get('text', '')
                    if search_word in text:
                        matching_words.append(text)

        except KeyError as ke:
            robot_print_error(f"Missing required key in response: {ke}")
            raise ValueError(f"Missing required key in response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in ocr_search: {e}")
            raise RuntimeError(f"Error in ocr_search: {e}")

    def ocr_search_string(self, test_case_name, search_word, interword_spaces=None, lang=None):
        """
        Search for a word in the OCR detections and return a list of words matching the letters from the JSON data.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param search_word: The word to search for.
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A list of words matching the letters from the JSON data.
        """
        try:

            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"

            self.interword_spaces = interword_spaces
            self.lang = lang

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            file_path = os.path.join(image_path, input_image)

            response = self.iVision_detect_url.send_request(
                url=self.url,
                file_path=file_path,
                bw_threshold=self.bw_threshold,
                ocr_output="string",
                interword_spaces=interword_spaces,
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=lang,
                region=self.region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            ).json()

            detections = response.get('result', {}).get('detections', [])
            matching_words = []

            for detection in detections:
                for item in detection.get('detection', []):
                    text = item.get('text', '')
                    if search_word in text:
                        matching_words.append(text)

            return matching_words

        except KeyError as ke:
            robot_print_error(f"Missing required key in response: {ke}")
            raise ValueError(f"Missing required key in response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in ocr_search_string: {e}")
            raise RuntimeError(f"Error in ocr_search_string: {e}")

    def ocr_search_string_debug(self, test_case_name, search_word, interword_spaces=None, lang=None):
        """
        Debug text detection using the test case name and save the input and output images.
        Search for a word in the OCR detections and return a list of words matching the letters from the JSON data.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param search_word: The word to search for.
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A dictionary with the input image path, detected image path, and search matches if successful.
        """
        try:
            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"
            self.interword_spaces = interword_spaces
            self.lang = lang

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            file_path = os.path.join(image_path, input_image)

            response = self.iVision_debug_url.send_request(
                url=self.debug_url,
                file_path=file_path,
                bw_threshold=self.bw_threshold,
                ocr_output="string",
                interword_spaces=str(self.interword_spaces),
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=str(self.lang),
                region=self.region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            )
            response_content_type = response.headers.get("content-type")
            robot_print_info(f"Response Content-Type: {response_content_type}")

            if response_content_type == "image/png":
                result_image_dir = self.iVision_Img.get_ivision_result_path()
                detected_image_path = os.path.join(result_image_dir, f"{search_word}_detected_image.png")

                with open(detected_image_path, "wb") as detected_file:
                    detected_file.write(response.content)

                robot_print_info(f"Detected image saved at: {detected_image_path}")
                return {
                    "message": "Images saved successfully",
                    "input_image_path": file_path,
                    "detected_image_path": detected_image_path,
                }

            else:
                raise ValueError(f"Unexpected response content type: {response_content_type}")

        except KeyError as ke:
            robot_print_error(f"A required key is missing in the request or response: {ke}")
            raise ValueError(f"A required key is missing in the request or response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in ocr_search_string_debug: {e}")
            raise RuntimeError(f"Error in ocr_search_string_debug: {e}")

    def ocr_detect_by_region(self, test_case_name, interword_spaces=None, lang=None, region=None, ocr_output=None):
        """
        Fetch text from the OCR detections based on the specified region.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param region: The region to search within (x, y, width, height).
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A list of words from the OCR response.
        """
        try:
            if region is None:
                raise ValueError("The 'region' parameter must be provided.")
            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"
            ocr_output = ocr_output if ocr_output is not None else self.ocr_output
            self.interword_spaces = interword_spaces
            self.lang = lang
            robot_print_info(f"region{region}")
            # breakpoint()

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            file_path = os.path.join(image_path, input_image)

            response = self.iVision_detect_url.send_request(
                url=self.url,
                file_path=file_path,
                bw_threshold=self.bw_threshold,
                # ocr_output=self.ocr_output,
                ocr_output=ocr_output,
                interword_spaces=interword_spaces,
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=lang,
                region=region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            ).json()

            detections = response.get('result', {}).get('detections', [])
            robot_print_info(f'detections: {detections}')

            matching_words = []
            robot_print_info(f'ocr_output :{ocr_output}')
            if ocr_output == 'data':
                for detection in detections:
                    for item in detection.get('detection', []):
                        text = item.get('text', '')
                        matching_words.append(text)
            elif ocr_output == 'string':
                for detection in detections:
                    for item in detection.get('detection'):
                        robot_print_info(f'item: {item}')
                        text_sentences = item.get('text_sentences')
                        robot_print_info(f'text_sentences: {text_sentences}')
                        # matching_words.append(text_sentences)
                        matching_words = matching_words + text_sentences

            return matching_words

        except KeyError as ke:
            robot_print_error(f"Missing required key in response: {ke}")
            raise ValueError(f"Missing required key in response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in OCR_detect_by_region: {e}")
            raise RuntimeError(f"Error in OCR_detect_by_region: {e}")

    def ocr_detect_debug_by_region(self, test_case_name, interword_spaces=None, lang=None, region=None):
        """
        Fetch text from the OCR detections based on the specified region and save the detected image.
        :param test_case_name: The test case name (used for fetching image folder path).
        :param region: The region to search within (x, y, width, height).
        :param interword_spaces: Interword spacing (provided in test case).
        :param lang: The language to use (provided in test case).
        :return: A dictionary with the input image path and detected image path if successful.
        """
        try:
            if region is None:
                raise ValueError("The 'region' parameter must be provided.")
            interword_spaces = interword_spaces if interword_spaces is not None else 0
            lang = lang if lang is not None else "eng"
            self.interword_spaces = interword_spaces
            self.lang = lang
            robot_print_info(f"region{region}")

            self.iVision_Img.set_ivision_test_case_folder(test_case_name)
            image_path = self.iVision_Img.get_ivision_image_path()

            input_images = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not input_images:
                raise FileNotFoundError(f"No input image found in {image_path}")

            input_image = input_images[0]
            input_image_path = os.path.join(image_path, input_image)

            response = self.iVision_debug_url.send_request(
                url=self.debug_url,
                file_path=input_image_path,
                bw_threshold=self.bw_threshold,
                ocr_output=self.ocr_output,
                interword_spaces=interword_spaces,
                preprocessing_algorithm=self.preprocessing_algorithm,
                psm=self.psm,
                lang=lang,
                region=region,
                confidence_threshold=self.confidence_threshold,
                oem=self.oem
            )

            response_content_type = response.headers.get("content-type")
            robot_print_info(f"Response Content-Type: {response_content_type}")

            if response_content_type == "image/png":
                result_image_dir = self.iVision_Img.get_ivision_result_path()
                detected_image_path = os.path.join(result_image_dir, f"{region}_detected_image.png")

                with open(detected_image_path, "wb") as detected_file:
                    detected_file.write(response.content)

                robot_print_info(f"Detected image saved at: {detected_image_path}")
                return {
                    "message": "Images saved successfully",
                    "input_image_path": input_image_path,
                    "detected_image_path": detected_image_path
                }

            else:
                raise ValueError(f"Unexpected response content type: {response_content_type}")

        except KeyError as ke:
            robot_print_error(f"A required key is missing in the request or response: {ke}")
            raise ValueError(f"A required key is missing in the request or response: {ke}")
        except Exception as e:
            robot_print_error(f"Error in OCR_detect_save_image_by_region: {e}")
            raise RuntimeError(f"Error in OCR_detect_save_image_by_region: {e}")

    def _verify_response(self, response, expected_box, text_name):
        """
        Verify the 'box' and 'text' values in the response.

        Args:
            response (dict): The response object containing detection data.
            expected_box (list): The expected bounding box values.
            text_name (str): The expected text to match.

        Returns:
            bool: True if a matching detection is found with sufficient confidence, False otherwise.
        """
        try:

            detections = response.get('result', {}).get('detections', [])

            for detection in detections:
                for item in detection.get('detection', []):
                    if (item.get('text') == text_name and
                            item.get('box') == expected_box and
                            item.get('confidence', 0) >= self.confidence):
                        return True

            return False

        except Exception as e:
            robot_print_error(f"An error occurred while verifying the response: {e}")
            return False

    def ocr_duration_verification(self, test_case_name, buffer_path, interword_spaces=None, lang=None, region=None,
                                  ocr_output=None,
                                  buffer_size=300):
        """ This function is created to verify duration of a warning or any message displayed in cluster.
            param test_case_name: The test case name (used for fetching image folder path).
            param region: The region to search within (x, y, width, height).
            param interword_spaces: Interword spacing (provided in test case).
            param lang: The language to use (provided in test case)
            param : buffer_size - Size of buffer / sample size

            return : returns duration of warning displayed.
            """

        try:
            self.initial_flag = 0
            self.final_flag = 0
            self.result = None
            files = self.list_files_in_folder(buffer_path)
            for i in range(1, int(buffer_size)):
                img_temp = os.path.join(buffer_path, files[i])
                robot_print_info(f"img_temp === {img_temp}")
                self.iVision_Img.set_ivision_test_case_folder(test_case_name)
                self.iVision_Img.ivision_input_image(img_temp)
                self.result = self.ocr_detect_by_region(test_case_name, interword_spaces, lang, region, ocr_output)
                robot_print_info(f'result == {self.result}')
                if i == 1:
                    if self.result != ['']:
                        robot_print_error(f"Warning detected in 1st frame can't calculate duration")
                else:
                    if self.result != [''] and self.initial_flag == 0:
                        self.initial_flag = i
                    if self.result == [''] and self.initial_flag:
                        self.final_flag = i
                if self.initial_flag and self.final_flag:
                    break
            robot_print_info(f"1st imge {files[self.initial_flag]} last img {files[self.final_flag]}")
            start_file = files[self.initial_flag]
            end_file = files[self.final_flag]
            duration = self.calculate_time_difference(start_file, end_file)
            return duration

        except Exception as e:
            robot_print_error(f"Exception occured in ocr_duration_verification {e}")
            return None

    def list_files_in_folder(self, buffer_path):
        """
        This function is created to list all files in a folder.
                return : list of files inside the folder
                """
        try:
            files = os.listdir(buffer_path)

            files = [f for f in files if os.path.isfile(os.path.join(buffer_path, f))]

            return files
        except Exception as e:
            robot_print_error(f"Exception occured {e}")
            return str(e)

    def extract_timestamp(self, filename):
        """
        args: filename - file name in below format
        This function Extracts the timestamp from a filename in the format:
        -1-08d_15h_54m_11.471-img-51405-.jpg
        Return: Returns the total time in seconds.
        """
        match = re.search(r'-\d+-(\d+)d_(\d+)h_(\d+)m_(\d+\.\d+)', filename)
        if match:
            days = int(match.group(1))
            hours = int(match.group(2))
            minutes = int(match.group(3))
            seconds = float(match.group(4))
            total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
            return total_seconds
        else:
            raise ValueError("Timestamp format not found in filename.")

    def calculate_time_difference(self, filename1, filename2):
        """
        This function Calculates the time difference in seconds between two filenames based on timestamp in name
        Args: Filename1 & filename2 - Two file names to calculate.
        Return: duration_seconds - Duration in seconds
        """
        time1 = self.extract_timestamp(filename1)
        time2 = self.extract_timestamp(filename2)
        duration_seconds = time2 - time1
        return duration_seconds
