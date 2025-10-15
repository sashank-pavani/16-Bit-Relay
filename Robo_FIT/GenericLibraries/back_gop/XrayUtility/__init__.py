import os
import logging
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ROBOT_REPORT_FOLDER_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass

common_class = CommonKeywordsClass()

file_path = os.path.join(common_class.get_report_path(), ROBOT_REPORT_FOLDER_NAME, "XrayUtilityLogs.log")

logging.basicConfig(
    filename=file_path,
    format="%(asctime)s\t%(name)s\t[%(module)s\t%(funcName)s\t%(lineno)d]\t%(levelname)s - \t%(message)s",
    filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
