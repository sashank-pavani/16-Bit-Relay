import inspect
import ntpath
import os
from pathlib import Path
import sys
import traceback
import logging
from colored import fg
from datetime import datetime
from pathlib import Path
from robot.api import logger as robot_logger
from robot.api import logger

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
END = "\033[0m"
UNDERLINE = "\033[4m"
YELLOW = "\033[1;33m"
WHITE = "\033[1;37m"


class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Reset color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = "\033[1;37m"


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: LogColors.WHITE + "%(asctime)s\t%(levelname)s\t%(message)s" + LogColors.ENDC,
        logging.INFO: LogColors.OKGREEN + "%(asctime)s\t%(levelname)s\t%(message)s" + LogColors.ENDC,
        logging.WARNING: LogColors.WARNING + "%(asctime)s\t%(levelname)s\t%(message)s" + LogColors.ENDC,
        logging.ERROR: LogColors.FAIL + "%(asctime)s\t%(levelname)s\t%(message)s" + LogColors.ENDC,
        logging.CRITICAL: LogColors.BOLD + LogColors.FAIL + "%(asctime)s\t%(levelname)s\t%(message)s" + LogColors.ENDC
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    __instance = None

    @staticmethod
    def get_logger_instance() -> 'Logger':
        if Logger.__instance is None:
            Logger()
        return Logger.__instance

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception(f"{__class__} is a singleton class")
        else:
            file_path = self.__get_robofit_log_file_path()
            self.__logger = logging.getLogger()
            self.__robot_logger = logging.getLogger("RobotFramework")
            self.__logger.setLevel(logging.DEBUG)
            self.__robot_logger.setLevel(logging.DEBUG)
            # formatter = logging.Formatter("%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")

            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(CustomFormatter())

            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(CustomFormatter())

            self.__logger.addHandler(file_handler)
            self.__logger.addHandler(stdout_handler)
            self.__robot_logger.addHandler(file_handler)
            Logger.__instance = self

    @property
    def logger(self):
        return self.__logger

    def get_log_level_value(self, log_type):
        if log_type == "ERROR":
            return logging.ERROR
        elif log_type == "DEBUG":
            return logging.DEBUG
        elif log_type == "INFO":
            return logging.INFO
        elif log_type == "WARNING":
            return logging.WARNING
        else:
            return logging.DEBUG

    def __custom_parent_directory(self, file_path, levels_up=1):
        path_obj = Path(file_path).resolve()
        for _ in range(levels_up):
            path_obj = path_obj.parent
        return str(path_obj)

    def __get_robofit_log_file_path(self):
        root_path = self.__custom_parent_directory(__file__, levels_up=5)
        return os.path.join(root_path, f"robofit_log_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log")


def __create_robot_message(log_level, msg, date):
    FORMATS = {
        "DEBUG": LogColors.WHITE + date + "\tDEBUG" + msg + LogColors.ENDC,
        "INFO": LogColors.OKGREEN + date + "\tINFO" + msg + LogColors.ENDC,
        "WARNING": LogColors.WARNING + date + "\tWARNING" + msg + LogColors.ENDC,
        "ERROR": LogColors.FAIL + date + "\tERROR" + msg + LogColors.ENDC,
        "CRITICAL": LogColors.BOLD + LogColors.FAIL + date + "\tCRITICAL" + msg + LogColors.ENDC
    }
    if log_level == "ERROR":
        robot_logger.error(FORMATS[log_level], html = True)
    elif log_level == "DEBUG":
        robot_logger.debug(FORMATS[log_level], html = True)
        robot_logger.console(FORMATS[log_level], newline = True)
    elif log_level == "INFO":
        robot_logger.info(FORMATS[log_level], html = True, also_console = True)
    elif log_level == "WARNING":
        robot_logger.warn(FORMATS[log_level], html = True)
    else:
        robot_logger.debug(FORMATS[log_level], html = True)



def __print(category, color, print_in_report, underline, log_type, date, text,
            class_name=None, function=None, line_number=None):
    """
    This method is use to print the logs
    :param category: 1 if print on report, 2 if print on Robot Report
    :param color: color to be used to print on console
                - Green: INFO
                - Red: ERROR
                - Yellow: WARNING
                - White: DEBUG
    :param print_in_report: True if print logs in console as well as on Robot Report
    :param underline: True if print logs underline
    :param log_type: Type of the logs ERROR, INFO, DEBUG, WARNING
    :param date: Timestamp of log
    :param text: Text to be print
    :param class_name: Name of caller class
    :param function: Caller function name
    :param line_number: Number of line where function call
    """
    reset = END
    logger_obj = Logger.get_logger_instance()
    if not class_name:
        class_name = ""
    else:
        path, class_name = ntpath.split(class_name)
        class_name = f"\tclass={class_name}"
    if not function:
        function = ""
    else:
        function = f"\tfunction={function}"
    if not line_number:
        line_number = ""
    else:
        line_number = f"\tline: {line_number}"
    if underline:
        un_line = UNDERLINE
        if category == 1:
            print(color + un_line + date + class_name + function + line_number + "\t" +
                  log_type + "\t" + str(text) + "\n" + reset)
        else:
            logger.console(
                "\n" + color + un_line + date + class_name + function + line_number + "\t" + log_type + "\t" + str(
                    text) + "\n" + reset)
    else:
        if category == 1:
            print(color + date + class_name + function + line_number + "\t" + log_type + "\t" + str(text) +
                  "\n" + reset)
        elif category == 2 and print_in_report:
            logger.console("\n" + color + date + class_name + function + line_number + "\t" + log_type + "\t" +
                           str(text) + "\n" + reset)
            print(color + date + class_name + function + line_number + "\t" + log_type + "\t" + str(text) +
                  "\n" + reset)
        else:
            logger.console("\n" + color + date + class_name + function + line_number + "\t" + log_type + "\t" +
                           str(text) + "\n" + reset)
    msg = f"{class_name} {function} {line_number}\t{str(text)}"
    __create_robot_message(log_type, msg, date)
    logger_obj.logger.log(level = logger_obj.get_log_level_value(log_type = log_type), msg = msg)
    if log_type == "ERROR":
        __print_error_line()


def __print_error_line():
    """
    Used to print the more info related to exception
    :return: None
    :rtype: None
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    if None not in [exc_type, exc_obj, exc_tb]:
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error = f"Error info: {exc_type, file_name, exc_tb.tb_lineno}\n\n{traceback.print_exc()}"
        print(error)
        # robot_logger.console("\n" + error)


def print_info(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type INFO on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = GREEN
    data = inspect.stack()[1]
    __print(category = 1, color = color, print_in_report = print_in_report, underline = underline, log_type = "INFO",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def print_error(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type ERROR on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = RED
    data = inspect.stack()[1]
    __print(category = 1, color = color, print_in_report = print_in_report, underline = underline, log_type = "ERROR",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def print_warning(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type WARNING on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = YELLOW
    data = inspect.stack()[1]
    __print(category = 1, color = color, print_in_report = print_in_report, underline = underline, log_type = "WARNING",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def print_debug(text: str, print_in_report: bool = False, underline: bool = False):
    """
    This method is used to print the logs type DEBUG in robot report
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = WHITE
    data = inspect.stack()[1]
    if os.environ['ROBOFIT_DEBUG_ENABLE'].lower() == "yes":
        __print(category = 1, color = color, print_in_report = print_in_report, underline = underline,
                log_type = "DEBUG", date = now,
                text = text, class_name = data[1], function = data[3], line_number = data[2])


def robot_print_info(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type INFO on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = GREEN
    data = inspect.stack()[1]
    __print(category = 2, color = color, print_in_report = print_in_report, underline = underline, log_type = "INFO",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def robot_print_debug(text: str, print_in_report: bool = False, underline: bool = False):
    """
    This method is used to print the logs type DEBUG on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = WHITE
    data = inspect.stack()[1]
    if os.environ['ROBOFIT_DEBUG_ENABLE'].lower() == "yes":
        __print(category = 2, color = color, print_in_report = print_in_report, underline = underline,
                log_type = "DEBUG", date = now,
                text = text, class_name = data[1], function = data[3], line_number = data[2])


def robot_print_warning(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type WARNING on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = YELLOW
    data = inspect.stack()[1]
    __print(category = 2, color = color, print_in_report = print_in_report, underline = underline, log_type = "WARNING",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def robot_print_error(text: str, print_in_report: bool = True, underline: bool = False):
    """
    This method is used to print the logs type ERROR on robot console
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    color = RED
    data = inspect.stack()[1]
    __print(category = 2, color = color, print_in_report = print_in_report, underline = underline, log_type = "ERROR",
            date = now,
            text = text, class_name = data[1], function = data[3], line_number = data[2])


def robot_custom_print(text: str, color: str, print_in_report: bool = False, underline: bool = False,
                       is_date: bool = True,
                       set_class_info: bool = True):
    """
    This method is used to print colored log as user provide arguments
    :param set_class_info: if you want to print class name line name and
    :param is_date: if user want to add date time to there print make it true else false
    :param color: color you want to print
    :param text: Test to be print
    :param print_in_report: True if user want to print the log on console as well Robot Report too
    :param underline: True if user want to underline log on the console.
    """
    color = fg(color)
    if is_date:
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S:%f")
    else:
        date = ""
    if set_class_info:
        data = inspect.stack()[1]
        class_name = data[1]
        function = data[3]
        line_number = data[2]
    else:
        class_name = None
        function = None
        line_number = None
    __print(category = 2, color = color, print_in_report = print_in_report, underline = underline, log_type = "INFO",
            date = date, text = text, class_name = class_name, function = function, line_number = line_number)
