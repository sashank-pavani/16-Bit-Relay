from CRE.Libraries.ProjectLibs.cVision.cVisionCamera.cVisionCam import cVisionCam
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from CRE.Libraries.ProjectLibs.cVision.Single_Circular_Gauge.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import (
    robot_print_error, robot_print_debug, robot_print_warning, robot_print_info
)

class Single_Circular_Gauge:
    def __init__(self):
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

    def find_boundary_lines(self, image, boundary_color):
        """Finds boundary lines in the cropped reference image based on the specified color."""
        try:
            robot_print_debug("Detecting boundary lines in the reference image...")

            # Convert the cropped image to HSV color space for color-based detection
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Convert the boundary color from BGR to HSV
            boundary_color_bgr = np.uint8([[boundary_color]])
            boundary_color_hsv = cv2.cvtColor(boundary_color_bgr, cv2.COLOR_BGR2HSV)[0][0]

            # Dynamically adjust tolerance based on boundary color hue
            hue_tolerance = 15 if boundary_color_hsv[0] < 10 else 10  # Lower hue tolerance for low hue values
            lower_bound = np.array([max(boundary_color_hsv[0] - hue_tolerance, 0), 50, 50])
            upper_bound = np.array([min(boundary_color_hsv[0] + hue_tolerance, 179), 255, 255])

            # Create a mask that identifies areas of the image that match the boundary color
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

            # Use morphological operations to clean up the mask (optional but helps with noise)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # Detect edges in the mask using the Canny edge detector
            edges = cv2.Canny(mask, 50, 150)

            # Detect lines in the edges using the Hough Line Transform
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)

            if lines is None or len(lines) < 2:
                robot_print_warning("Could not detect two boundary lines in the reference image.")
                raise ValueError("Could not detect two boundary lines in the reference image.")

            # Convert detected lines to a more usable format and filter them
            detected_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                angle = np.arctan2((y2 - y1), (x2 - x1)) * 180 / np.pi  # Convert angle to degrees

                # Filter for lines that are near-horizontal and long enough
                if 85 < abs(angle) < 95:  # Close to 90 degrees (horizontal lines)
                    detected_lines.append((x1, y1, x2, y2))

            # Sort the detected lines based on their x-coordinates (left to right)
            detected_lines = sorted(detected_lines, key=lambda line: line[0])

            if len(detected_lines) < 2:
                robot_print_warning("Insufficient valid boundary lines detected.")
                raise ValueError("Insufficient valid boundary lines detected.")

            start_boundary = detected_lines[0]  # Leftmost line
            end_boundary = detected_lines[-1]  # Rightmost line

            robot_print_info("Boundary lines detected successfully in the cropped reference image.")
            return start_boundary, end_boundary

        except Exception as e:
            robot_print_error(f"Error in detecting boundary lines in the cropped reference image: {str(e)}")
            raise

    def find_gauge_circle(self, image):
        """Detects the gauge circle in the image."""
        try:
            robot_print_debug("Detecting gauge circle...")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=50, maxRadius=300)

            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                robot_print_info(f"Gauge circle detected at position: {circles[0]}")
                return circles[0]
            else:
                robot_print_warning("No circular gauge detected in the image.")
                raise ValueError("Could not detect a circular gauge in the image.")
        except Exception as e:
            robot_print_error(f"Failed to detect gauge circle: {str(e)}")
            raise

    def find_needle_tip(self, image, gauge_center):
        """Finds the needle tip in the actual image."""
        try:
            robot_print_debug("Detecting needle tip...")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

            if lines is None:
                robot_print_warning("No needle found in the actual image.")
                raise ValueError("No needle found in the actual image.")

            max_distance = -1
            needle_tip = None
            for line in lines:
                for x1, y1, x2, y2 in line:
                    dist1 = np.linalg.norm(np.array([x1, y1]) - np.array(gauge_center))
                    dist2 = np.linalg.norm(np.array([x2, y2]) - np.array(gauge_center))
                    if dist1 > max_distance:
                        max_distance = dist1
                        needle_tip = (x1, y1)
                    if dist2 > max_distance:
                        max_distance = dist2
                        needle_tip = (x2, y2)

            robot_print_info(f"Needle tip detected at: {needle_tip}")
            return needle_tip
        except Exception as e:
            robot_print_error(f"Failed to detect needle tip: {str(e)}")
            raise

    def calculate_needle_angle(self, start_boundary, needle_point, center_point):
        try:
            # Vector for 0-degree line (start boundary to center)
            zero_degree_vector = np.array([start_boundary[0] - center_point[0], start_boundary[1] - center_point[1]])
            # Vector for needle line (needle tip to center)
            needle_vector = np.array([needle_point[0] - center_point[0], needle_point[1] - center_point[1]])

            # Normalize the vectors to have unit length
            zero_degree_vector = zero_degree_vector / np.linalg.norm(zero_degree_vector)
            needle_vector = needle_vector / np.linalg.norm(needle_vector)

            # Use atan2 to calculate the angle for both lines with respect to the center
            start_angle = np.arctan2(zero_degree_vector[1], zero_degree_vector[0])  # 0-degree line
            needle_angle = np.arctan2(needle_vector[1], needle_vector[0])  # Needle line

            # Convert from radians to degrees
            start_angle_deg = np.degrees(start_angle)
            needle_angle_deg = np.degrees(needle_angle)

            # Calculate the difference between the angles
            angle_deg = (needle_angle_deg - start_angle_deg) % 360

            # Ensure the angle is always calculated clockwise
            if angle_deg < 0:
                angle_deg += 360

            return angle_deg
        except Exception as e:
            robot_print_error(f"Error in calculating needle angle: {str(e)}")
            raise

    def draw_gauge_visualization(self, image, gauge_circle, start_boundary, end_boundary, needle_tip, needle_angle,
                                 center_point, reference_image, result_filename):
        try:
            x, y, r = gauge_circle
            cv2.circle(image, (x, y), r, (255, 0, 0), 2)  # Draw the gauge circle (blue)
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Mark the center point (green)

            # Draw the start boundary line (green)
            cv2.line(image, (start_boundary[0], start_boundary[1]), (start_boundary[2], start_boundary[3]), (0, 255, 0),
                     2)

            # Draw the end boundary line (red)
            cv2.line(image, (end_boundary[0], end_boundary[1]), (end_boundary[2], end_boundary[3]), (0, 0, 255), 2)

            # Draw the needle tip (red)
            cv2.circle(image, needle_tip, 5, (0, 0, 255), -1)

            # Draw a line from the center of the gauge to the needle tip
            cv2.line(image, (x, y), needle_tip, (0, 0, 0), 2)  # Needle line (black)

            # Draw the 0-degree line from the center to the start of the boundary
            start_x1, start_y1 = start_boundary[0], start_boundary[1]
            cv2.line(image, (x, y), (start_x1, start_y1), (255, 0, 255), 2)  # 0-degree line (purple)

            # Label the 0-degree position on the start boundary
            text_position = (start_boundary[0] + 10, start_boundary[1] - 10)  # Position for 0-degree text
            cv2.putText(image, "0 degrees", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # Label the angle near the needle
            angle_position = (needle_tip[0] + 10, needle_tip[1])
            cv2.putText(image, f"{needle_angle:.2f} degrees", angle_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0),
                        2)

            # Draw the arc
            arc_radius = 50  # You can adjust this value for arc size
            arc_center = (x, y)  # Center of the gauge

            # Calculate the start and end angles based on the coordinates
            start_angle = np.degrees(np.arctan2(start_y1 - y, start_x1 - x))  # Angle of the 0-degree line
            end_angle = np.degrees(np.arctan2(needle_tip[1] - y, needle_tip[0] - x))  # Angle of the needle line

            # Normalize angles to be in the range [0, 360)
            start_angle = start_angle % 360
            end_angle = end_angle % 360

            # Draw the arc
            cv2.ellipse(image, arc_center, (arc_radius, arc_radius), 0, start_angle, end_angle, (255, 255, 0),
                        2)  # Arc (yellow)

            # Visualization plotting
            plt.figure(figsize=(10, 5))

            # Reference image with detected boundaries
            plt.subplot(1, 2, 1)
            plt.imshow(cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB))
            plt.title("Reference Image with Detected Boundaries")
            plt.axis('off')

            # Actual image with detected needle and gauge visualization
            plt.subplot(1, 2, 2)
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            plt.title("Actual Image with Needle and Gauge Visualization")
            plt.axis('off')

            plt.tight_layout()

            # Get the result path and ensure the directory exists
            result_path = os.path.join(self.cam.get_cvision_result_path(), result_filename + ".jpg")
            result_dir = os.path.dirname(result_path)
            os.makedirs(result_dir, exist_ok=True)  # Create directory if it doesn't exist

            # Save the figure
            plt.savefig(result_path)
            plt.show()

        except Exception as e:
            robot_print_error(f"Error in drawing gauge visualization: {str(e)}")
            raise

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

    def process_images(self, test_case_name: str, reference_key: str):
        try:
            # Set the test case folder
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

            # Find the boundary lines in the cropped reference image using the color from the config
            start_boundary, end_boundary = self.find_boundary_lines(reference_image, boundary_line_color)

            gauge_circle = self.find_gauge_circle(final_cropped_image)

            # Find the needle tip in the actual image
            center_point = (gauge_circle[0], gauge_circle[1])  # Center of the circle
            needle_tip = self.find_needle_tip(final_cropped_image, center_point)

            # Calculate the angle between the 0-degree line and the needle line
            needle_angle = self.calculate_needle_angle(start_boundary, needle_tip, center_point)

            robot_print_info(f"Needle Angle: {needle_angle:.2f} degrees")


            # Draw the gauge, boundaries, needle, and visualization on the actual image
            self.draw_gauge_visualization(actual_image, gauge_circle, start_boundary, end_boundary, needle_tip,
                                          needle_angle, center_point, reference_image, result_filename)

            return needle_angle
        except Exception as e:
            robot_print_error(f"Error in processing images: {str(e)}")
            # Ensure the image is saved even on failure
            self.save_failed_visualization(actual_image, reference_image, None, result_filename)