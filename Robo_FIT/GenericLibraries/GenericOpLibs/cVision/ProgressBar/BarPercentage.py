from CRE.Libraries.ProjectLibs.cVision.ProgressBar.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)

from CRE.Libraries.ProjectLibs.cVision.cVisionCamera.cVisionCam import cVisionCam
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


class BarPercentage:
    def __init__(self):
        """Initializes the BarPercentage class and its components."""
        try:
            self.detected_percentage = None
            self.test_case_name = None
            self.cam = cVisionCam()
            self.config_manager = ConfigurationManager()
            robot_print_info("BarPercentage initialized.")
        except Exception as e:
            robot_print_error(f"Initialization failed: {str(e)}")
            raise

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
            image = cv2.imread(image_path)
            if image is None:
                robot_print_error(f"Error: Could not load image from path: {image_path}")
                raise ValueError(f"Error: Could not load image from path: {image_path}")
            robot_print_info(f"Loaded image from: {image_path}")
            return image
        except Exception as e:
            robot_print_error(f"Failed to load image: {str(e)}")
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
                # Resize template to current scale
                scaled_template = cv2.resize(gray_template, (0, 0), fx=scale, fy=scale)

                # Skip the scale if the template becomes larger than the main image
                if scaled_template.shape[0] > gray_main_image.shape[0] or scaled_template.shape[1] > \
                        gray_main_image.shape[1]:

                    continue

                # Perform template matching
                result = cv2.matchTemplate(gray_main_image, scaled_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                # Update best match if this one is better
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
            max_loc = match
            tH, tW = template.shape[:2]

            startX, startY = max_loc
            endX, endY = startX + tW, startY + tH

            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

            return image
        except Exception as e:
            robot_print_error(f"Failed to draw bounding box: {str(e)}")
            raise

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
            max_loc = match
            tH, tW = template.shape[:2]

            startX, startY = max_loc
            final_cropped_image = image[startY:startY + tH, startX:startX + tW]

            return final_cropped_image
        except Exception as e:
            robot_print_error(f"Failed to crop image: {str(e)}")
            raise

    def detect_segments(self, image):
        """Detects segments in the given image by finding contours.

                Args:
                    image (np.ndarray): The input image in which to detect segments.

                Returns:
                    list: A list of tuples, each containing the bounding box coordinates (x, y, width, height) of detected segments.
        """
        try:
            edges = cv2.Canny(image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            segments = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                segments.append((x, y, w, h))

            robot_print_info(f"Detected {len(segments)} segments.")
            return segments
        except Exception as e:
            robot_print_error(f"Segment detection failed: {str(e)}")
            raise

    def generate_hsv_range(self, rgb_color, hue_variation=10, sat_variation=50, val_variation=50):
        """
        Generate HSV lower and upper bounds from RGB color.
        """
        # Convert RGB to HSV
        hsv_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HSV)[0][0]

        # Create lower and upper bounds based on variations
        lower_bound = np.array([
            max(0, hsv_color[0] - hue_variation),  # Ensure hue doesn't go below 0
            max(0, hsv_color[1] - sat_variation),  # Ensure saturation doesn't go below 0
            max(0, hsv_color[2] - val_variation)   # Ensure value doesn't go below 0
        ])

        upper_bound = np.array([
            min(180, hsv_color[0] + hue_variation),  # Ensure hue doesn't go above 180 (in OpenCV)
            min(255, hsv_color[1] + sat_variation),  # Ensure saturation doesn't go above 255
            min(255, hsv_color[2] + val_variation)   # Ensure value doesn't go above 255
        ])

        return lower_bound, upper_bound

    def calculate_filled_percentage(self, segment_img, ref_img_bar_key):
        try:
            hsv_img = cv2.cvtColor(segment_img, cv2.COLOR_BGR2HSV)

            # Calculate the total number of pixels in the segment image
            total_pixels = segment_img.shape[0] * segment_img.shape[1]

            # Retrieve the foreground and background RGB colors dynamically using the ref_img_bar_key
            fg_rgb_color = self.config_manager.get_fg_color(ref_img_bar_key)
            bg_rgb_color = self.config_manager.get_bg_color(ref_img_bar_key)

            # Generate the HSV ranges for the foreground and background colors
            fg_lower, fg_upper = self.generate_hsv_range(fg_rgb_color)
            bg_lower, bg_upper = self.generate_hsv_range(bg_rgb_color)

            # Create masks for foreground and background
            mask_fg = cv2.inRange(hsv_img, fg_lower, fg_upper)
            mask_bg = cv2.inRange(hsv_img, bg_lower, bg_upper)

            # Neglect background pixels in the foreground mask
            mask_fg = cv2.bitwise_and(mask_fg, mask_fg, mask=~mask_bg)

            # Count the non-zero pixels in the foreground mask
            fg_pixels = cv2.countNonZero(mask_fg)

            # If there are no foreground pixels, return 0%
            if fg_pixels == 0:
                return 0, 'empty'

            # Calculate the filled percentage based on the foreground pixels
            filled_percentage = (fg_pixels / total_pixels) * 100
            robot_print_info(f"Segment filled percentage: {filled_percentage:.2f}%")

            return filled_percentage, 'colored'

        except Exception as e:
            robot_print_error(f"Failed to calculate filled percentage: {str(e)}")
            raise

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
            axes[0].set_title('Reference Bar Gauge')
            axes[0].axis('off')

            axes[1].imshow(cv2.cvtColor(setup_image, cv2.COLOR_BGR2RGB))
            axes[1].set_title('Actual Setup Image with Detection')
            axes[1].axis('off')

            axes[2].imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            axes[2].set_title('Detected Bar Gauge (Cropped)')
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

    def process_bar_percentage(self, test_case_name: str, ref_img_bar_key: str):
        try:
            # Set the test case folder
            self.cam.set_cVision_test_case_folder(test_case_name)

            # Get the result path and ensure the directory exists
            result_path = self.cam.get_cvision_result_path()
            os.makedirs(result_path, exist_ok=True)

            # Retrieve the reference image path from the ConfigurationManager using the provided key
            reference_image_path = self.config_manager.get_reference_image_path(ref_img_bar_key)

            # Automatically load the setup image from the cVision_CamImg folder
            setup_image_path = os.path.join(self.cam.get_cvision_image_path(), 'Img.jpg')

            # Load the setup image and reference image
            setup_image = self.load_image(setup_image_path)
            reference_image = self.load_image(reference_image_path)

            # Process the images with template matching
            match, best_val = self.template_matching(setup_image, reference_image)
            if match is None:
                robot_print_error("Bar gauge detection failed.")

                # Visualize and save failed attempt
                segment_details = "Bar gauge detection failed"
                result_filename = f"bar_percentage_failure_{ref_img_bar_key}"
                self.visualize_images(reference_image, setup_image, setup_image, segment_details, result_filename)

                # Save at least some image showing the failure
                return

            # Draw bounding box around the detected area
            setup_image_with_rectangle = self.draw_bounding_box(setup_image.copy(), match, reference_image)

            # Crop the image to the detected bar gauge size
            cropped_image = self.crop_to_reference_size(setup_image, match, reference_image)

            # Detect segments in the cropped image
            segments = self.detect_segments(cropped_image)

            segment_fill_percentages = []
            total_percentage = 0
            num_segments = len(segments)

            for i, (x, y, w, h) in enumerate(segments):
                segment_img = cropped_image[y:y + h, x:x + w]
                percentage, segment_type = self.calculate_filled_percentage(segment_img, ref_img_bar_key)

                if segment_type == 'colored':
                    segment_fill_percentages.append(f"Segment {i + 1}: Filled ({percentage:.2f}%)")
                    total_percentage += (percentage / 100) * (100 / num_segments)
                else:
                    segment_fill_percentages.append(f"Segment {i + 1}: Empty (0%)")

                # Draw green boxes around detected segments in the cropped image
                cv2.rectangle(cropped_image, (x, y), (x + w, y + h), (0, 255, 0), 1)

            self.detected_percentage = total_percentage  # Store the total bar percentage
            robot_print_info(f"Total Bar Percentage: {total_percentage:.2f}%")
            segment_details = f"Total Bar Percentage: {total_percentage:.2f}%"

            # Visualize and save the images and results
            result_filename = f"bar_percentage_result_{ref_img_bar_key}"
            self.visualize_images(reference_image, setup_image_with_rectangle, cropped_image, segment_details,
                                  result_filename)

            return total_percentage

        except Exception as e:
            robot_print_error(f"Unexpected error in process_bar_percentage: {str(e)}")

            # Save images even if there's an exception
            result_filename = f"bar_percentage_error_{ref_img_bar_key}"
            segment_details = f"Error during processing: {str(e)}"
            self.visualize_images(reference_image, setup_image, setup_image, segment_details, result_filename)

            raise

