import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from CRE.Libraries.ProjectLibs.cVision.CurvedProgressBar.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)

from CRE.Libraries.ProjectLibs.cVision.cVisionCamera.cVisionCam import cVisionCam

class CurvedBarPercentage:
    def __init__(self):
        """Initializes the BarPercentage class and its components."""
        try:

            self.detected_percentage = None
            self.test_case_name = None
            self.cam = cVisionCam()
            self.config_manager = ConfigurationManager()
            robot_print_info("CurvedBarPercentage initialized.")
        except Exception as e:
            robot_print_error(f"Error initializing CurvedBarPercentage class: {str(e)}")


    def load_image(self, image_path):
        """Loads an image from the specified path.

                Args:
                    image_path (str): The path to the image file.

                Returns:
                    np.ndarray: The loaded image as a NumPy array.

                Raises:
                    ValueError: If the image cannot be loaded.
        """
        try:
            robot_print_debug(f"Attempting to load image from path: {image_path}")
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(
                    f"Error: Could not load image from path: {image_path}. Please check the path and file format.")
            robot_print_info(f"Successfully loaded image from path: {image_path}")
            return image
        except Exception as e:
            robot_print_error(f"Error loading image from path {image_path}: {str(e)}")
            raise

    def template_matching(self, main_image, template, scales=None):
        """Performs template matching to find the best match of the template in the main image.

                        Args:
                            main_image (np.ndarray): The main image where the template is searched.
                            template (np.ndarray): The template image to match.
                            scales (list, optional): List of scales to resize the template for matching.

                        Returns:
                            tuple: Coordinates of the best match and the best matching value.

                        Raises:
                            Exception: If template matching fails.
        """
        try:
            gray_main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            if scales is None:
                scales = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]

            best_match = None
            best_max_val = -1
            best_max_loc = None

            # Perform multi-scale template matching
            for scale in scales:

                scaled_template = cv2.resize(gray_template, (0, 0), fx=scale, fy=scale)


                if scaled_template.shape[0] > gray_main_image.shape[0] or scaled_template.shape[1] > \
                        gray_main_image.shape[1]:

                    continue

                # Perform template matching
                result = cv2.matchTemplate(gray_main_image, scaled_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val > best_max_val:
                    best_max_val = max_val
                    best_max_loc = max_loc
                    best_match = (max_loc, scale)

            threshold = 0.7  # Adjust this threshold if needed
            if best_max_val < threshold:

                return None, None


            return best_max_loc, best_max_val

        except Exception as e:
            robot_print_error(f"Template matching failed: {str(e)}")
            return None, None

    def draw_bounding_box(self, image, match, template):
        """Draws a bounding box around the detected match in the image.

                Args:
                    image (np.ndarray): The image where the bounding box is to be drawn.
                    match (tuple): The coordinates of the match.
                    template (np.ndarray): The template image used for drawing the box.

                Returns:
                    np.ndarray: The image with the bounding box drawn.
        """
        try:
            if match is None:
                return image

            max_loc = match
            tH, tW = template.shape[:2]
            startX, startY = max_loc
            endX, endY = startX + tW, startY + tH

            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            return image
        except Exception as e:
            robot_print_error(f"Error drawing bounding box: {str(e)}")
            return image

    def crop_to_reference_size(self, image, match, template):
        """Crops the image to the size of the detected template.

                Args:
                    image (np.ndarray): The original image to crop from.
                    match (tuple): The coordinates of the detected match.
                    template (np.ndarray): The template image for determining the crop size.

                Returns:
                    np.ndarray: The cropped image.
        """
        try:
            if match is None:
                return image

            max_loc = match
            tH, tW = template.shape[:2]
            startX, startY = max_loc
            final_cropped_image = image[startY:startY + tH, startX:startX + tW]
            return final_cropped_image
        except Exception as e:
            robot_print_error(f"Error cropping image: {str(e)}")
            return image

    def create_markers(self, image):
        """Creates markers for the watershed algorithm using image segmentation.

            Args:
                image (np.ndarray): The input image to create markers from.

            Returns:
                np.ndarray: The markers image.

            Raises:
                Exception: If marker creation fails.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            sure_bg = cv2.dilate(binary, kernel, iterations=3)

            dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, cv2.THRESH_BINARY)

            sure_fg = np.uint8(sure_fg)
            sure_bg = np.uint8(sure_bg)
            unknown = cv2.subtract(sure_bg, sure_fg)

            ret, markers = cv2.connectedComponents(sure_fg)
            markers += 1
            markers[unknown == 255] = 0
            return markers
        except Exception as e:
            robot_print_error(f"Error creating markers: {str(e)}")
            return None

    def apply_watershed(self, image, markers):
        """
           Applies the watershed algorithm to segment the image using the provided markers.

           Args:
               image (np.ndarray): The input image.
               markers (np.ndarray): The markers created from segmentation.

           Returns:
               tuple: The image with segmented boundaries and the updated markers.

           Raises:
               Exception: If the watershed algorithm fails.
        """
        try:
            markers = cv2.watershed(image, markers)
            image[markers == -1] = [0, 255, 0]
            return image, markers
        except Exception as e:
            robot_print_error(f"Error applying watershed algorithm: {str(e)}")
            return image, markers

    def create_color_mask(self, image, lower_color, upper_color):
        """
            Creates a binary mask based on the specified color range.

            Args:
                image (np.ndarray): The input image.
                lower_color (np.ndarray): The lower bound of the color range in HSV.
                upper_color (np.ndarray): The upper bound of the color range in HSV.

            Returns:
                np.ndarray: The binary mask for the specified color range.

            Raises:
                Exception: If creating the color mask fails.
        """
        try:
            hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_img, lower_color, upper_color)
            return mask
        except Exception as e:
            robot_print_error(f"Error creating color mask: {str(e)}")
            return None

    def generate_hsv_range(self, rgb_color, hue_variation=10, sat_variation=50, val_variation=50):
        """
            Generates an HSV range from an RGB color with specified variations.

            Args:
                rgb_color (np.ndarray): The input RGB color.
                hue_variation (int, optional): The allowed variation in hue. Default is 10.
                sat_variation (int, optional): The allowed variation in saturation. Default is 50.
                val_variation (int, optional): The allowed variation in value. Default is 50.

            Returns:
                tuple: The lower and upper bounds of the HSV range.

            Raises:
                None
            """
        # Convert RGB to HSV
        hsv_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HSV)[0][0]

        # Create lower and upper bounds based on variations
        lower_bound = np.array([
            max(0, hsv_color[0] - hue_variation),
            max(0, hsv_color[1] - sat_variation),
            max(0, hsv_color[2] - val_variation)
        ])

        upper_bound = np.array([
            min(180, hsv_color[0] + hue_variation),
            min(255, hsv_color[1] + sat_variation),
            min(255, hsv_color[2] + val_variation)
        ])

        return lower_bound, upper_bound

    def calculate_filled_percentage(self, image, markers, color_mask):
        """
            Calculates the percentage of the filled area based on the provided color mask and segmented markers.

            Args:
                image (np.ndarray): The input image.
                markers (np.ndarray): The segmented markers created by the watershed algorithm.
                color_mask (np.ndarray): The mask of the detected color.

            Returns:
                float: The percentage of the filled area.

            Raises:
                Exception: If the calculation fails.
            """
        try:
            total_percentage = 0
            num_segments = len(np.unique(markers)) - 1

            for label in np.unique(markers)[1:]:
                segment_mask = np.where(markers == label, 255, 0).astype(np.uint8)
                color_in_segment = cv2.bitwise_and(color_mask, color_mask, mask=segment_mask)

                filled_area = cv2.countNonZero(color_in_segment)
                total_area = cv2.countNonZero(segment_mask)
                if total_area > 0:
                    total_percentage += (filled_area / total_area)

            if num_segments > 0:
                self.detected_percentage = (total_percentage / num_segments) * 100
            else:
                self.detected_percentage = 0

            robot_print_info(f"Calculated filled percentage: {self.detected_percentage:.2f}%")
            return self.detected_percentage
        except Exception as e:
            robot_print_error(f"Error calculating filled percentage: {str(e)}")
            return 0

    def visualize_images(self, reference_image, setup_image, cropped_image, segment_details, result_filename):
        """
            Visualizes and saves the reference, detected, cropped images, and results.

            Args:
                reference_image (np.ndarray): The reference image of the curved bar.
                setup_image (np.ndarray): The detected setup image with bounding box.
                cropped_image (np.ndarray): The cropped image based on template matching.
                segment_details (str): The filled percentage or other details to display.
                result_filename (str): The name for saving the result visualization.

            Returns:
                None

            Raises:
                Exception: If visualization fails.
        """
        try:
            fig, axes = plt.subplots(1, 4, figsize=(20, 5))

            axes[0].imshow(cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB))
            axes[0].set_title('Reference CurvedBar Gauge')
            axes[0].axis('off')

            axes[1].imshow(cv2.cvtColor(setup_image, cv2.COLOR_BGR2RGB))
            axes[1].set_title('Actual Setup Image with Detection')
            axes[1].axis('off')

            axes[2].imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            axes[2].set_title('Detected CurvedBar Gauge (Cropped)')
            axes[2].axis('off')

            axes[3].text(0.5, 0.5, segment_details, fontsize=15, ha='center')
            axes[3].axis('off')

            plt.tight_layout()

            # Get the result path and ensure the directory exists
            result_path = os.path.join(self.cam.get_cvision_result_path(), result_filename + ".jpg")
            result_dir = os.path.dirname(result_path)
            os.makedirs(result_dir, exist_ok=True)  # Create directory if it doesn't exist

            # Save the figure
            plt.savefig(result_path)
            plt.show()

            robot_print_info(f"Result visualization saved at: {result_path}")
        except Exception as e:
            robot_print_error(f"Failed to visualize images: {str(e)}")
            raise

    def process_curved_bar_percentage(self, test_case_name: str, reference_image_key: str):
        """
           Processes the bar percentage detection and calculates the filled percentage for detected segments.

           Args:
               reference_image_key (str): The key to retrieve the reference image and color configurations.

           Returns:
               float: The total percentage of the bar filled.

           Raises:
               Exception: If processing fails.
        """
        try:
            self.cam.set_cVision_test_case_folder(test_case_name)
            # Get the reference image path using the provided key
            reference_image_path = self.config_manager.get_reference_image_path(reference_image_key)

            # Retrieve foreground and background colors from the configuration
            foreground_color = np.array(self.config_manager.get_fg_color(reference_image_key), dtype=np.uint8)
            background_color = np.array(self.config_manager.get_bg_color(reference_image_key), dtype=np.uint8)

            # Print the colors for debugging
            robot_print_info(f"Foreground color from JSON: {foreground_color}")
            robot_print_info(f"Background color from JSON: {background_color}")

            # Automatically load the captured image from the cVision_CamImg folder
            setup_image_path = os.path.join(self.cam.get_cvision_image_path(), 'Img.jpg')

            # Load the setup image and reference image
            setup_image = self.load_image(setup_image_path)
            reference_image = self.load_image(reference_image_path)

            # Initialize placeholders for images in case of early exit due to failure
            detected_image = setup_image.copy()
            cropped_image = setup_image.copy()

            # Process the images with template matching
            match, best_val = self.template_matching(setup_image, reference_image)

            if match is None:
                robot_print_error("Curved bar gauge detection failed.")
                # Visualize the failed case by saving the setup and reference images without further processing
                segment_details = "Detection failed. No match found."
                result_filename = f"bar_percentage_result_failed_{reference_image_key}"
                self.visualize_images(reference_image, setup_image, cropped_image, segment_details, result_filename)
                return

            # Draw bounding box and crop to reference size
            detected_image = self.draw_bounding_box(setup_image, match, reference_image)
            cropped_image = self.crop_to_reference_size(detected_image, match, reference_image)

            # Create markers and apply watershed algorithm
            markers = self.create_markers(cropped_image)
            output_image, markers = self.apply_watershed(cropped_image, markers)

            # Generate HSV range for the foreground color
            lower_foreground_color, upper_foreground_color = self.generate_hsv_range(foreground_color)

            # Create color mask for the foreground using the generated HSV ranges
            foreground_mask = self.create_color_mask(output_image, lower_foreground_color, upper_foreground_color)

            # Optionally: Create a mask for the background using its color range
            lower_background_color, upper_background_color = self.generate_hsv_range(background_color)
            background_mask = self.create_color_mask(output_image, lower_background_color, upper_background_color)

            # Calculate filled percentage using the foreground mask
            filled_percentage = self.calculate_filled_percentage(output_image, markers, foreground_mask)

            # Prepare visualization segment details
            segment_details = f"Filled Percentage: {filled_percentage:.2f}%"

            # Visualize and save the images and results
            result_filename = f"bar_percentage_result_{reference_image_key}"
            self.visualize_images(reference_image, detected_image, cropped_image, segment_details, result_filename)

            robot_print_info(f"Filled percentage processed successfully: {filled_percentage:.2f}%")
            return filled_percentage

        except Exception as e:
            robot_print_error(f"Error processing curved bar percentage: {str(e)}")
            try:
                # In case of failure, visualize the images and save them for debugging purposes
                segment_details = "Processing failed due to an exception."
                result_filename = f"bar_percentage_result_failed_{reference_image_key}"
                self.visualize_images(reference_image, detected_image, cropped_image, segment_details, result_filename)
            except Exception as vis_error:
                robot_print_error(f"Failed to visualize images during error handling: {str(vis_error)}")

            return None
