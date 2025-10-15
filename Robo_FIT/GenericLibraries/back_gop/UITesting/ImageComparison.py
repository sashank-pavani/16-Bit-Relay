import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from skimage.metrics import structural_similarity as ssim


class ImageComparison:

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()

    def mse(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err

    def compare(self, imageA: list, imageB: list):

        x1 = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        x2 = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        absdiff = cv2.absdiff(x1, x2)

        diff = cv2.subtract(x1, x2)
        result = not np.any(diff)

        m = self.mse(x1, x2)
        s = ssim(x1, x2)
        print("mse: %s, ssim: %s" % (m, s))

        return s, absdiff

    def compare_accuracy(self, absdiff: list, result: int, accuracy: int, test_name: str, identifier: str)-> bool:

        if (result * 100) > int(accuracy)-1:
            print("The images are the same")
            return True
        else:

            cv2.imwrite(os.path.join(self.common_keyword.get_module_folder(), "ActualImages",
                                     test_name.split(" ")[0] + "ActualImage_" + identifier + ".png"),
                        absdiff)
            print("The images are different")
            return False
