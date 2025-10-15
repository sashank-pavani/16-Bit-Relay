import os
import logging
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ROBOT_REPORT_FOLDER_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info, robot_print_error

common_class = CommonKeywordsClass()

log_dir = os.path.join(common_class.get_report_path(), ROBOT_REPORT_FOLDER_NAME)
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
        robot_print_info(f"Created log directory: {log_dir}")
    except Exception as e:
        robot_print_error(f"Failed to create log directory: {e}")

file_path = os.path.join(log_dir, "XrayUtilityLogs.log")

try:
    handler = logging.FileHandler(file_path, mode='w')
    formatter = logging.Formatter(
        "%(asctime)s\t%(name)s\t[%(module)s\t%(funcName)s\t%(lineno)d]\t%(levelname)s - \t%(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
except Exception as e:
    robot_print_error(f"Error configuring logging: {e}")
