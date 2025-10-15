import numpy as np

from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.ImageComparison import ImageComparison
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.ImageProcessor import *
# from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywords import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
import os
import cv2


class UiTesterClass:

    def __init__(self):
        self.compare = ImageComparison()
        self.common_keyword = CommonKeywordsClass()
        self.project_config = ProjectConfigManager()
        # path is "Project_W601/res/Images/"
        self.image_path = os.path.join(self.common_keyword.get_root_path(), self.project_config.get_project_name(),
                                       CRE_LIBRARIES, CRE_RESOURCES, CRE_IMAGES)

    def compare_default_screen(self, imageA: str, imageB: str, accuracy: int, test_name: str, identifier: str) -> bool:
        '''
        Compare two original images without excluding any region
        :param identifier: unique id in case of same testcase
        :param imageA: Path of image to be compared with
        :param imageB: Path of image of the current screen
        :param accuracy: Accuracy percentage
        :param test_name: ${TEST_NAME} from Robot
        :return: Boolean (True/False)
        '''
        imA = cv2.imread(os.path.join(self.image_path, imageA))
        imB = cv2.imread(imageB)

        result, absdiff = self.compare.compare(imA, imB)

        output = self.compare.compare_accuracy(absdiff, result, int(accuracy), test_name, identifier)

        return output

    def compare_region_of_interest(self, image: str, screenshot: str, coordinates: str, accuracy: int, test_name: str,
                                   identifier: str) -> bool:
        '''
        To find a specific region of interest in the current screen
        :param identifier: unique id in case of same testcase
        :param image: path of image to compare with
        :param screenshot: path of image taken at the time of execution
        :param coordinates: {StartX, StartY, EndX, EndY}
                 startX: X coordinate of top left point of region to be excluded
                 startY: Y coordinate of top left point of region to be excluded
                 endX:  X coordinate of bottom right point of region to be excluded
                 endY:  Y coordinate of bottom right point of region to be excluded
        :param accuracy: Accuracy percentage
        :param test_name: ${TEST_NAME} from Robot
        :return: Boolean (True/False)
        '''
        im = cv2.imread(os.path.join(self.image_path, image))
        ss = cv2.imread(screenshot)
        coordinates = coordinates.split(" ")
        tmp = ss[int(coordinates[1]):int(coordinates[3]), int(coordinates[0]):int(coordinates[2])]

        image_size = im.shape[:2]
        template_size = tmp.shape[:2]

        print('image_size (y,x)', image_size)
        print('template_size (y,x)', template_size)

        result = cv2.matchTemplate(im, tmp, cv2.TM_SQDIFF)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        topleftx = min_loc[0]
        toplefty = min_loc[1]
        sizex = template_size[1]
        sizey = template_size[0]

        im_tmp = im[toplefty: toplefty + sizey, topleftx: topleftx + sizex]

        result, absdiff = self.compare.compare(tmp, im_tmp)

        output = self.compare.compare_accuracy(absdiff, result, int(accuracy), test_name, identifier)

        if not output:
            font = cv2.FONT_HERSHEY_SIMPLEX
            org = (50, 50)
            fontScale = 3
            color = (0, 0, 255)
            thickness = 3
            screenshot = cv2.putText(ss, 'Image not matched', org, font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.rectangle(ss, (int(coordinates[0]), int(coordinates[1])), (int(coordinates[2]), int(coordinates[3])),
                          (0, 0, 255), 2)

            cv2.imwrite(os.path.join(self.common_keyword.get_module_folder(), "ActualImages",
                                     test_name.split(" ")[0] + "error_" + identifier + ".png"), screenshot)
        return output

    def compare_static_area_multiple(self, imageA: str, imageB: str, coordinates: str, accuracy: int, test_name: str,
                                     identifier: str) -> bool:
        '''
        Compare screen by excluding multiple dynamic region
        :param identifier: unique id in case of same testcase
        :param imageA: Path of image to be compared
        :param imageB: Path of image of the current screen
        :param coordinates: {StartX, StartY, EndX, EndY, StartX, StartY, EndX, EndY} Array of coordinates of multiple regions
        :param accuracy: Accuracy percentage
        :param test_name: ${TEST_NAME} from Robot
        :return: Boolean (True/False)
        '''
        imA = cv2.imread(os.path.join(self.image_path, imageA))
        imB = cv2.imread(imageB)
        coordinates = coordinates.split(" ")

        for i in range(0, int((len(coordinates) / 4))):
            imA = get_icon_rect(imA, int(coordinates[i * 4]), int(coordinates[i * 4 + 1]), int(coordinates[i * 4 + 2]),
                                int(coordinates[i * 4 + 3]))
            imB = get_icon_rect(imB, int(coordinates[i * 4]), int(coordinates[i * 4 + 1]), int(coordinates[i * 4 + 2]),
                                int(coordinates[i * 4 + 3]))

        result, absdiff = self.compare.compare(imA, imB)

        output = self.compare.compare_accuracy(absdiff, result, int(accuracy), test_name, identifier)

        return output

    def find_image_in_screen(self, template: str, image: str, accuracy: int = 80) -> list:
        '''
        Search for an template image in a complete image
        :param template: Smaller image (icon/button)
        :param image: Original complete screen/image
        :param accuracy: Accuracy percentage
        :return: array of Coordinates for the template found in image
        '''
        print(f"find image path : {template}, {image}")
        img_rgb = cv2.imread(image)

        # Convert it to grayscale
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        # Read the template
        template = cv2.imread(template, 0)

        # Store width and height of template in w and h
        w, h = template.shape[::-1]

        # Perform match operations.
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

        # Specify a threshold
        threshold = (accuracy / 100) - 0.2

        # Store the coordinates of matched area in a numpy array
        loc = np.where(res >= threshold)
        coordinate = []
        # Draw a rectangle around the matched region.
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)
            coordinate = [pt, (pt[0] + w, pt[1] + h)]

        # Show the final image with the matched area.
        # cv2.imshow('Detected', img_rgb)
        print(f"Coordinates in find image: {coordinate}")
        # cv2.waitKey(0)
        return coordinate
