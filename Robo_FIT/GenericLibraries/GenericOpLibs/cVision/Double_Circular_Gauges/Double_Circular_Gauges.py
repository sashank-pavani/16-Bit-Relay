import cv2
import numpy as np
import matplotlib.pyplot as plt
from CRE.Libraries.ProjectLibs.cVision.Double_Circular_Gauges.ConfigurationManager import ConfigurationManager
from CRE.Libraries.ProjectLibs.cVision.cVisionCamera.cVisionCam import cVisionCam
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)
import os

class Double_Circular_Gauges:
    def __init__(self):
        # Initialize ConfigurationManager in the constructor
        self.config_manager = ConfigurationManager()
        self.test_case_name = None
        self.cam = cVisionCam()

    def load_image(self, image_path):
        """Loads an image from the specified path."""
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
        """Draws a bounding box around the detected match."""
        try:
            max_loc = match
            tH, tW = template.shape[:2]
            startX, startY = max_loc
            endX, endY = startX + tW, startY + tH
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            robot_print_info(f"Drew bounding box from ({startX}, {startY}) to ({endX}, {endY})")
            return image
        except Exception as e:
            robot_print_error(f"Failed to draw bounding box: {str(e)}")
            raise

    def crop_to_reference_size(self, reference_image, match, actual_image):
        try:
            # Assuming match contains the top-left corner of the best match area
            max_loc = match  # Update this line based on your template matching result structure
            if max_loc is None:
                robot_print_error("No match found for cropping.")
                return None  # Return None if no valid match found

            startX, startY = max_loc
            # Define your crop area; you may need to adjust the sizes based on your images
            endX = startX + reference_image.shape[1]
            endY = startY + reference_image.shape[0]

            # Crop the image
            cropped_image = actual_image[startY:endY, startX:endX]
            return cropped_image

        except Exception as e:
            robot_print_error(f"Failed to crop image: {str(e)}")
            return None

    def find_boundary_lines_near_gauge(self, image, gauge_circle, boundary_color):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Convert boundary color to HSV
        boundary_color_bgr = np.uint8([[boundary_color]])  # Create a dummy image for conversion
        boundary_color_hsv = cv2.cvtColor(boundary_color_bgr, cv2.COLOR_BGR2HSV)[0][0]

        lower_bound = np.array([boundary_color_hsv[0] - 10, 40, 40])
        upper_bound = np.array([boundary_color_hsv[0] + 10, 255, 255])

        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        edges = cv2.Canny(mask, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)

        if lines is None or len(lines) < 2:
            raise ValueError("Could not detect two boundary lines near the gauge.")

        # Filter lines that are close to the gauge center
        x, y, r = gauge_circle
        filtered_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dist1 = np.linalg.norm(np.array([x1, y1]) - np.array([x, y]))
            dist2 = np.linalg.norm(np.array([x2, y2]) - np.array([x, y]))
            if dist1 < r * 1.5 or dist2 < r * 1.5:
                filtered_lines.append(line)

        if len(filtered_lines) < 2:
            raise ValueError("Could not detect enough boundary lines near the gauge.")

        filtered_lines = sorted(filtered_lines, key=lambda line: line[0][0])
        start_boundary = filtered_lines[0][0]  # The first line
        end_boundary = filtered_lines[-1][0]  # The last line

        return start_boundary, end_boundary

    def find_two_gauge_circles(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=15, minRadius=50,
                                   maxRadius=300)

        if circles is not None and len(circles[0]) >= 2:
            circles = np.round(circles[0, :2]).astype("int")
            return circles
        else:
            raise ValueError("Could not detect exactly two circular gauges in the image.")

    def find_needle_tip(self, actual_image, gauge_circle, is_left_gauge=True):
        gray = cv2.cvtColor(actual_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply a circular mask to focus on the gauge area
        mask = np.zeros_like(gray)
        x, y, r = gauge_circle
        cv2.circle(mask, (x, y), r, 255, thickness=-1)
        edges = cv2.bitwise_and(edges, edges, mask=mask)

        # Clean up the edges using morphological operations
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Use separate Hough Line Transform parameters for left and right gauges
        if is_left_gauge:
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=70, maxLineGap=20)
        else:
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=60, maxLineGap=15)

        if lines is None:
            raise ValueError("No needle found in the actual image.")

        # Filter lines based on proximity and directionality from the center
        max_length = -1
        needle_tip = None
        for line in lines:
            for x1, y1, x2, y2 in line:
                length = np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))
                dist1 = np.linalg.norm(np.array([x1, y1]) - np.array([x, y]))
                dist2 = np.linalg.norm(np.array([x2, y2]) - np.array([x, y]))

                # Check if the line is pointing outward from the center and within the gauge radius
                if length > max_length and dist1 < r and dist2 < r:
                    max_length = length
                    needle_tip = (x1, y1) if dist1 > dist2 else (x2, y2)

        if needle_tip is None:
            raise ValueError("Needle tip not found within the gauge.")

        return needle_tip

    def calculate_needle_angle(self, start_boundary, needle_point, center_point, is_left_gauge=True):
        zero_degree_vector = np.array([start_boundary[0] - center_point[0], start_boundary[1] - center_point[1]])
        needle_vector = np.array([needle_point[0] - center_point[0], needle_point[1] - center_point[1]])

        zero_degree_vector = zero_degree_vector / np.linalg.norm(zero_degree_vector)
        needle_vector = needle_vector / np.linalg.norm(needle_vector)

        start_angle = np.arctan2(zero_degree_vector[1], zero_degree_vector[0])
        needle_angle = np.arctan2(needle_vector[1], needle_vector[0])

        start_angle_deg = np.degrees(start_angle)
        needle_angle_deg = np.degrees(needle_angle)

        # Calculate the angle difference between the needle and the 0-degree line
        angle_deg = (needle_angle_deg - start_angle_deg) % 360

        # Handle different starting points for left and right gauges
        if not is_left_gauge:
            angle_deg = (angle_deg + 180) % 360  # Adjust for right-side gauge starting point

        # Handle the case where the needle is exactly on the 0-degree line
        if np.isclose(needle_angle_deg, start_angle_deg, atol=1e-2):
            angle_deg = 0.0  # Return 0 degrees when the needle aligns with the start

        return angle_deg

    def draw_gauge_visualization(self, image, gauge_circle, start_boundary, end_boundary, needle_tip, needle_angle, center_point):
        x, y, r = gauge_circle
        cv2.circle(image, (x, y), r, (255, 0, 0), 3)
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        cv2.line(image, (start_boundary[0], start_boundary[1]), (start_boundary[2], start_boundary[3]), (0, 255, 0), 3)
        cv2.line(image, (end_boundary[0], end_boundary[1]), (end_boundary[2], end_boundary[3]), (0, 0, 255), 3)

        cv2.circle(image, needle_tip, 5, (0, 0, 255), -1)
        cv2.line(image, (x, y), needle_tip, (0, 0, 0), 2)

        start_x1, start_y1 = start_boundary[0], start_boundary[1]
        cv2.line(image, (x, y), (start_x1, start_y1), (255, 0, 255), 2)

        text_position = (start_boundary[0] + 10, start_boundary[1] - 10)
        cv2.putText(image, "0 degrees", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 3)

        angle_position = (needle_tip[0] + 10, needle_tip[1])
        cv2.putText(image, f"{needle_angle:.2f} degrees", angle_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 0, 255), 3)

        arc_radius = 50
        arc_center = (x, y)

        start_angle = np.degrees(np.arctan2(start_y1 - y, start_x1 - x))
        end_angle = np.degrees(np.arctan2(needle_tip[1] - y, needle_tip[0] - x))

        start_angle = start_angle % 360
        end_angle = end_angle % 360

        cv2.ellipse(image, arc_center, (arc_radius, arc_radius), 0, start_angle, end_angle, (255, 255, 0), 3)

    def save_failed_visualization(self, actual_image, reference_image, cropped_image, result_filename):
        """Saves the failed visualization including the cropped image even if the test case fails."""
        try:
            result_path = os.path.join(self.cam.get_cvision_result_path(), result_filename + "_failed.jpg")
            result_dir = os.path.dirname(result_path)
            os.makedirs(result_dir, exist_ok=True)

            plt.figure(figsize=(15, 5))

            # Reference image
            plt.subplot(1, 3, 1)
            plt.imshow(cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB))
            plt.title("Reference Image")
            plt.axis('off')

            # Actual image
            plt.subplot(1, 3, 2)
            plt.imshow(cv2.cvtColor(actual_image, cv2.COLOR_BGR2RGB))
            plt.title("Actual Image (Failed)")
            plt.axis('off')

            # Cropped image
            plt.subplot(1, 3, 3)
            if cropped_image is not None:
                plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                plt.title("Cropped Image")
            else:
                plt.text(0.5, 0.5, 'Cropped Image Not Available', horizontalalignment='center',
                         verticalalignment='center', fontsize=12, color='red')
                plt.title("Cropped Image")
            plt.axis('off')

            plt.tight_layout()
            plt.savefig(result_path)
            plt.show()

            robot_print_info(f"Failed test case visualization (including cropped image) saved to {result_path}")

        except Exception as e:
            robot_print_error(f"Error saving failed visualization: {str(e)}")


    def process_double_circular_gauge(self, test_case_name: str,reference_key):
        try:
            # Set the test case folder in cVisionCam

            self.cam.set_cVision_test_case_folder(test_case_name)

            # Get the result path and ensure the directory exists
            result_path = self.cam.get_cvision_result_path()
            os.makedirs(result_path, exist_ok=True)

            # Use the ConfigurationManager to read the reference image path and boundary color
            reference_image_path = self.config_manager.get_reference_image_path(reference_key)
            boundary_line_color = self.config_manager.get_boundary_line_color(reference_key)

            # Automatically load the setup image from the cVision_CamImg folder
            setup_image_path = os.path.join(self.cam.get_cvision_image_path(), 'Img.jpg')

            # Load the setup image and reference image
            actual_image = self.load_image(setup_image_path)
            reference_image = self.load_image(reference_image_path)

            result_filename = f"gauge_detection_result_{reference_key}.png"
            match, best_val = self.template_matching(actual_image, reference_image)
            if match is None:
                robot_print_error("Bar gauge detection failed.")
                self.save_failed_visualization(actual_image, reference_image, None, result_filename)
                return

            # Crop to reference size using the template match result
            final_cropped_image = self.crop_to_reference_size(reference_image, match, actual_image)

            gauge_circles = self.find_two_gauge_circles(final_cropped_image)

            for gauge_circle in gauge_circles:
                center_point = (gauge_circle[0], gauge_circle[1])

                start_boundary, end_boundary = self.find_boundary_lines_near_gauge(reference_image, gauge_circle, boundary_line_color)
                needle_tip = self.find_needle_tip(final_cropped_image, gauge_circle)
                needle_angle = self.calculate_needle_angle(start_boundary, needle_tip, center_point)

                robot_print_info(f"Needle Angle: {needle_angle:.2f} degrees")
                self.draw_gauge_visualization(actual_image, gauge_circle, start_boundary, end_boundary, needle_tip, needle_angle,
                                         center_point)


        except Exception as e:

            robot_print_error(f"Error in processing images: {str(e)}")
            # Ensure the image is saved even on failure
            self.save_failed_visualization(actual_image, reference_image, None, result_filename)

            raise
