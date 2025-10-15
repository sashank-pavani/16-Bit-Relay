import os
import cv2
import imutils
import numpy as np
import json
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_warning, robot_print_info
from glob import glob
from PIL import Image
import subprocess
class ImageFinder:
    """
    initialize the list of reference points and boolean indicating
    whether cropping is being performed or not
    """

    def __init__(self):
        self.clone = None
        self.reference_image_path = None
        self.image = None
        self.roi = None
        self.result = None
        self.image_path = None
        self.roi_rect = {
            'x1': 0,
            'y1': 0,
            'x2': 0,
            'y2': 0
        }
        self.mouseX = 0
        self.mouseY = 0
        self.cropping = False

    def update_coordinates(self, json_file, crop_name, roi):
        """
            creates a json file and saves the co-ordinates of ROI after cropping is completed
            params json_file string : path of the json file to be saved
            crop_name string: json file name
            roi     int  :  roi co-ordinates
        """
        if not os.path.exists(json_file):
            with open(json_file, 'w') as fp:
                fp.write('')

        with open(json_file, 'r') as fp:
            data = fp.read()

        try:
            json_data = json.loads(data)
            json_data[crop_name] = roi
        except Exception as e:
            json_data = {crop_name: roi}

        with open(json_file, 'w') as fp:
            fp.write(json.dumps(json_data, indent=2))

    def is_img_in_img(self, image='', template='', threshold=.92, show=False, mark=False, use_crop=True):
        """ The Method used to check if the Template image present in the Screenshot image
             Returns the matched co-ordinates if image is inside template image
             params image string: path for the screenshot image
             template  string: path where the template image should get saved, if the image already present then give the specified path
             threshold  decimal/int: Accuracy for the comparison, depends on the clarity of the screenshot Image captured
             show  boolean: set it to True if the cropped image has to be shown in the execution
             mark  boolean: if required set it to True , marks the identified Image in the screenshot Image
             use_crop boolean: Asks for cropping

        """
        """ Returns if image is inside template image """
        robot_print_info(f'Screenshot Image path:{image}')
        '''Check if the two images exist'''
        if not os.path.isfile(image):
            robot_print_error(f'IMAGE FILE MISSING:{os.path.abspath(image)}')
            return 0

        if not os.path.isfile(template):
            if use_crop:
                ref_img_name = str(os.path.basename(template).split('.')[0])
                robot_print_info(f"ref_img_name:{ref_img_name}")
                ref_img_ext = str(os.path.basename(template).split('.')[1])
                robot_print_info(f"ref_img_ext:{ref_img_ext}")
                template_dir = os.path.abspath(os.path.dirname(template))
                robot_print_info(ref_img_name, ref_img_ext, template_dir)
                if not os.path.exists(template_dir):
                    os.mkdir(template_dir)
                    robot_print_debug(f"Template directory created at:{template_dir}")
                result = self.generate_reference_image(image, show_crop=True, crop_name=ref_img_name,
                                                       crop_ext=ref_img_ext,
                                                       template_dir=template_dir)
                if not result[0]:
                    robot_print_error(f'TEMPLATE FILE MISSING:{os.path.abspath(template)}')
                    return 0

            else:
                robot_print_error(f'TEMPLATE FILE MISSING:{os.path.abspath(template)}')
                return 0
        robot_print_info(f"template Image path:{template}")
        '''Load Images'''
        img_rgb = cv2.imread(image)

        """image rescaling process start"""
        # scale_percent = 80  # percent of original size
        scale_percent = 80  # percent of original size
        width = int(img_rgb.shape[1] * scale_percent / 100)
        height = int(img_rgb.shape[0] * scale_percent / 100)
        dim = (width, height)
        """resize image """
        img_rgb = cv2.resize(img_rgb, dim, interpolation=cv2.INTER_AREA)
        """image rescaling process end """

        template = cv2.imread(template)
        h, w = template.shape[:-1]
        '''Compare images'''
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        threshold = .98  # Defined as Function parameter
        loc = np.where(res >= threshold)
        coordinates = list(zip(*loc))
        robot_print_info(f"Coordinates of matched reference image in screenshot image:{coordinates}")
        my_result = [lis for lis in coordinates]
        if mark:
            '''Create rectangle if found'''
            for pt in zip(*loc[::-1]):
                # Switch columns and rows
                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 1)

            cv2.imwrite(self.image, img_rgb)

        if show:
            '''Show image with rectangle'''
            cv2.imshow(self.image, img_rgb)
            cv2.waitKey(0)
        robot_print_info(f"My_return_value:{len(list(zip(*loc)))}")
        if len(list(zip(*loc))) > 0:
            robot_print_info("Template Image exists in the screenshot image,Please check for the match Coordinates in "
                             "report")
        else:
            robot_print_error("Template Image does not exists in the Screenshot image")
        res = []
        for tup in my_result:
            res.append(tup[-1])
            res.append(tup[0])
        robot_print_info(f"Testing the result----{res}----")
        # robot_print_info(res[0:2])
        # return res[0:2]
        return res


    def click_and_crop(self, event, x, y, flags, param):
        """
            Method sets the mouse call back and helps user to crop the template image in the screenshot image
            records the starting and ending coordinates of the cropped image
            This method is called inside is_img_in_img method and in turn handled
        """
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv2.EVENT_LBUTTONDOWN:
            self.roi_rect['x1'] = x
            self.roi_rect['y1'] = y
            self.cropping = True
        # check to see if the left mouse button was released
        elif event == cv2.EVENT_MOUSEMOVE:
            self.mouseX, self.mouseY = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            self.roi_rect['x2'] = x
            self.roi_rect['y2'] = y
            self.cropping = False

    def bound_box_text(self, image, text='', font=cv2.FONT_HERSHEY_SIMPLEX, text_scale=0.5, tickness=1, alpha=0.8,
                       box_color=(255, 255, 255), text_color=(0, 0, 0), x=0, y=0):
        """
            This method is used to create a Text message around the screenshot image while cropping in order to guide the user
            for next steps
            params image string: Screenshot image path
            text  string: text message displayed on the screen
        """
        (test_width, text_height), baseline = cv2.getTextSize(text, font, text_scale, tickness)
        x1 = x
        y1 = y
        x2 = x1 + test_width
        y2 = y1 - text_height - baseline
        image_cpy = self.image.copy()
        cv2.rectangle(self.image, (x1, y1 + 5), (x2, y2), box_color, -1)
        cv2.putText(self.image, text, (x1, y1 - int(baseline / 2)), font, text_scale, text_color, tickness)

        return cv2.addWeighted(self.image, alpha, image_cpy, 1 - alpha, gamma=0)

    def generate_reference_image(self, image_path=None, show_crop=False, crop_name='CROPPED_IMAGE', crop_ext='png',
                                 template_dir=''):
        """
            Method creates the Template image directory and saves the template Image with default name CROPPED_IMAGE.png
            params image_path string: screenshot Image path
            show_crop  string: boolean , shows the cropped image
            crop_name string: Template Image file name
            crop_ext  string: png
            template_dir string: template/cropped image directory
        """
        self.mouseX = 0
        self.mouseY = 0
        self.cropping = False
        self.result = False

        # If not image provided exit the function
        if not image_path:
            return False
        if not os.path.exists(template_dir):
            os.mkdir(template_dir)
            robot_print_debug(f"Template directory created at:{template_dir}")

        # load the image, clone it, and setup the mouse callback function
        self.image = cv2.imread(image_path)

        # image rescaling process start
        scale_percent = 80  # percent of original size
        width = int(self.image.shape[1] * scale_percent / 100)
        height = int(self.image.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        self.image = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        # image rescaling process end
        self.clone = self.image.copy()
        if self.clone is None:
            robot_print_error("clone value is empty,Failed to load the Image")
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.click_and_crop)
        font = cv2.FONT_HERSHEY_SIMPLEX

        while True:

            if self.cropping:
                # Construct the region of interest rectangle
                if (self.mouseX, self.mouseY) != (0, 0):
                    self.roi_rect['x2'] = self.mouseX
                    self.roi_rect['y2'] = self.mouseY

            self.image = self.clone.copy()
            # if the region of interest is different of the default
            if self.roi_rect != {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}:
                if self.roi_rect.get('x1') - self.roi_rect.get('x2') < 0 and self.roi_rect.get(
                        'y1') - self.roi_rect.get('y2') < 0:
                    cv2.rectangle(self.image, (self.roi_rect.get('x1'), self.roi_rect.get('y1')),
                                  (self.roi_rect.get('x2'), self.roi_rect.get('y2')),
                                  (0, 255, 0), 1)
                    self.image = self.bound_box_text(self.image,
                                                     text='(x1: %i, y1: %i)' % (
                                                         self.roi_rect.get('x1'), self.roi_rect.get('y1')),
                                                     x=self.roi_rect.get('x1') - 80,
                                                     y=self.roi_rect.get('y1') - 15)
                    self.image = self.bound_box_text(self.image,
                                                     text='(x2: %i, y2: %i)' % (
                                                         self.roi_rect.get('x2'), self.roi_rect.get('y2')),
                                                     x=self.roi_rect.get('x2') + 5,
                                                     y=self.roi_rect.get('y2') - 5)

            if not self.cropping:
                # Mouse coordinates
                cv2.putText(self.image, 'x: %i, y: %i' % (self.mouseX, self.mouseY),
                            (self.mouseX + 10, self.mouseY - 20),
                            font, 0.8,
                            (255, 255, 255))
                # Instructions
                self.image = self.bound_box_text(self.image, "Instructions", text_scale=0.7, tickness=2, x=10, y=40)
                self.image = self.bound_box_text(self.image, "Select your ROI", x=10, y=63)
                self.image = self.bound_box_text(self.image, "press \"c\" to create crop", x=10, y=86)
                self.image = self.bound_box_text(self.image, "press \"q\" to exit", x=10, y=109)
            cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

            cv2.imshow("image", self.image)
            key = cv2.waitKey(1) & 0xFF
            # if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
                self.image = self.clone.copy()
                self.roi_rect = {
                    'x1': 0,
                    'y1': 0,
                    'x2': 0,
                    'y2': 0
                }
            # if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
                # if exist ROI
                try:

                    if self.roi_rect != {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0} and show_crop:

                        # Open window with crop image
                        try:
                            cv2.destroyWindow("Reference Image")
                        except:
                            pass

                        self.roi = self.clone[self.roi_rect["y1"]:self.roi_rect["y2"],
                                   self.roi_rect["x1"]:self.roi_rect["x2"]]

                        cv2.imshow("Reference Image", self.roi)
                    self.result = True
                except Exception as e:
                    robot_print_error(f"error raised: {e}")
            elif key == ord("q"):
                break
        if self.roi is None:
            robot_print_error(f"received None value for the ROI-:{self.roi}")
        if any(value < 0 for value in self.roi_rect.values()):
            robot_print_error("Invalid ROI coordinates: ", self.roi_rect)
        if self.result:
            # Create Reference Image
            try:
                output_path = os.path.join(template_dir, f"{crop_name}.{crop_ext}")
                self.reference_image_path = cv2.imwrite(output_path, self.roi)
            except Exception as e:
                robot_print_error(f"error in {e}")
            # save coordinates of ROI
            file_path = os.path.join(template_dir, "images_coord.json")
            self.update_coordinates(file_path, crop_name, self.roi_rect)

        # close all open windows
        cv2.destroyAllWindows()

        return self.result, self.roi_rect, self.roi

    def coordinates_json(self, path):
        """
            returns the list of co-ordinates from the json file that is saved while cropping
            params path string: path of the json file
        """
        with open(path) as f:
            data = json.load(f)
            first_value = list(data.values())[0]
            x = first_value['x1']
            y = first_value['y1']
            z = list()
            z.append(x)
            z.append(y)
        robot_print_info(f"Co-Ordinates from the saved reference image json file:{z}")
        return z

    # def compare_coords(self,list_a, list_b):
    #     return all(item in list_b for item in list_a)

    def compare_coords(self, list_a, list_b, range_value=1):
        for item_a in list_a:
            for item_b in list_b:
                if item_a - range_value <= item_b <= item_a + range_value:
                    return True
        return False

    def input_data(self):
        """
        The method is for taking the parameters to call the generate_reference_image from command execution
        """
        robot_print_info("Function called generate_reference_image and please give below information")
        image_path = input("\nPath to the image:")
        show_crop = bool(input("\nShow crop option(type True/False):"))
        crop_name = input("\nName of the cropped image(default=CROPPED_IMAGE):")
        crop_ext = input("\nExtension of the cropped image:")
        template_dir = input("\nPath to the template directory:")
        imageobj = ImageFinder()
        imageobj.generate_reference_image(
            image_path, show_crop, crop_name, crop_ext, template_dir
        )
