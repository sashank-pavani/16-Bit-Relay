import os
import sys
from typing import Union
from time import sleep
from robot.api import logger
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info, \
    robot_print_debug


class CommonKeywordsClass:
    """
    This class has common methods that use across ROBOFit Framework
    """
    TEAM_NAME = ""
    REPORT_PATH = ""
    TEST_MODULE_FOLDER = ""
    ROOT_DIRECTORY = None

    def __init__(self):
        pass

    def check_team_name(self, team_name: str) -> bool:
        """
        This method is used to check the Team name is valid or not
        :param team_name: Name of the team provided by user at time of execution
        :type team_name:Sting
        :return: True if given team name is valid, Otherwise False
        :rtype: Bool
        """
        try:
            robot_print_debug(f"Setting team name as : {team_name}")
            if team_name.upper() == SWE4:
                self.team_name = TEAM_SWE4
                return True
            elif team_name.upper() == SWE5:
                self.team_name = TEAM_SWE5
                robot_print_debug(f"TEAM NAME Set as : {self.team_name}")
                return True
            elif team_name.upper() == SWE6:
                self.team_name = TEAM_SWE6
                return True
            elif team_name.upper() == SYS5:
                self.team_name = TEAM_SYS5
                return True
            elif team_name.upper() == SYS4:
                self.team_name = TEAM_SYS4
                return True
            elif team_name.upper() == ROBOT_SCRIPT_NAME:
                self.team_name = TEAM_ROBOT_SCRIPT
            return False
        except Exception as exp:
            robot_print_error(f"Error to check the team name as EXCEPTION: {exp}")

    def set_root_directory(self, root_path):
        if CommonKeywordsClass.ROOT_DIRECTORY is None:
            CommonKeywordsClass.ROOT_DIRECTORY = os.path.join(root_path)
            if not os.path.isdir(CommonKeywordsClass.ROOT_DIRECTORY):
                raise OSError(f"The given path {root_path} is not a directory or a valid path")
            os.environ['ROBOT_ROOT_PATH'] = CommonKeywordsClass.ROOT_DIRECTORY

    @property
    def team_name(self):
        """
        This function is getter function and return the value of Team name
        :return: name of the team
        :rtype: String
        """
        return os.environ['TEAM_NAME']

    @team_name.setter
    def team_name(self, team_name: str):
        """
        This is an setter function and uset to set the team name
        :param team_name: Name of the team
        :type team_name: String
        :return: None
        :rtype: None
        """
        os.environ["TEAM_NAME"] = team_name
        robot_print_info(f"Team name as: {os.environ['TEAM_NAME']}")

    def get_root_path(self) -> str:
        """
        This method give the path of execution 'sh' file. i.e. test_execution.sh
        :return: <home_path>/test_execution.sh
        """
        try:
            return os.environ["ROBOT_ROOT_PATH"]
        except KeyError as key_err:
            robot_print_error(f"ROBOT_ROOT_PATH is not set in environment, EXCEPTION: {key_err}")

    def get_project_config_path(self):
        """
        This method gives the path of project_config_file.json.
        :return: <root_path>/CRE/Libraries/Resources/project_config_file.json
        :exception: If file not found the it will raise the FileNotFoundError.
        """
        robot_print_debug(f"Project config: {id(CommonKeywordsClass)}, TEAM NAME: {os.environ['TEAM_NAME']}")
        path = os.path.join(self.get_root_path(), PROJECT, os.environ["TEAM_NAME"], PROJECT_CONFIG,
                            PROJECT_CONFIG_FILE)
        robot_print_debug(f"Project Config Path: {path}")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"project_config_file.json doesnt found under the "
                                    f"team area: {os.environ['TEAM_NAME']}")
        return path

    def create_report_path(self, team_name: str, report_name: str) -> str:
        """
        This method create the path of newly creating report file. i.e Project_<date>_<time>
        :parameter team_name: name of the team
        :parameter report_name: Name of the Report i.e Project_SW<buildnumber>_<date>_<time>
        :return <home_path>/CRE/<TEAMNAME>/Test_Reports/<projectname>_<date>_<time>
        """
        try:
            CommonKeywordsClass.REPORT_PATH = os.path.join(self.get_root_path(), PROJECT, team_name,
                                                           TEST_REPORTS, report_name)
            if not os.path.isdir(CommonKeywordsClass.REPORT_PATH):
                os.makedirs(CommonKeywordsClass.REPORT_PATH, mode=0o777)
            os.environ["ROBOT_REPORT_PATH"] = CommonKeywordsClass.REPORT_PATH
            robot_print_info(f"Report path set as : {os.environ['ROBOT_REPORT_PATH']}")
            return CommonKeywordsClass.REPORT_PATH
        except Exception as exp:
            robot_print_error(f"Error to create the project report folder, EXCEPTION: {exp}")
            return ""

    def get_report_path(self) -> str:
        """
        This method provide the path of newly creating report file. i.e Project_<date>_<time>
        :return: <home_path>/Test_Report/Project_<date>_<time>
        :exception: FileNotFoundError
        """
        try:
            return os.environ["ROBOT_REPORT_PATH"]
        except KeyError as key_err:
            robot_print_error(f"ROBOT_REPORT_PATH is not set as environment variable, EXCEPTION: {key_err}")

    def get_module_folder(self):
        """
        This method provide the path of module report folder
        :param module: name of the module which use to create the file
        This parameter is passed from the robot file because robot provide the Module name
        :return: <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>
        """
        # TODO: module parameter remove
        try:
            return os.environ["TEST_MODULE_FOLDER"]
        except KeyError as key_err:
            robot_print_error(f"TEST_MODULE_FOLDER environment variable not set, EXCEPTION: {key_err}")

    def create_module_directory(self, module: str):
        """
        This method create the different folders which used to save the logs, screenshots, Custom report
        :param module: name of the module in which all the folder is created.

        for eg. :
            <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>
            <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot
            <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Custom_Reports

        """
        try:
            CommonKeywordsClass.TEST_MODULE_FOLDER = os.path.join(self.get_report_path(), module)
            if not os.path.isdir(CommonKeywordsClass.TEST_MODULE_FOLDER):
                os.makedirs(CommonKeywordsClass.TEST_MODULE_FOLDER, mode=0o777, exist_ok=True)
            os.makedirs(os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, ROBO_LOGS_SCREENSHOT), mode=0o777,
                        exist_ok=True)
            os.makedirs(os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, ROBO_ACTUAL_IMAGE), mode=0o777,
                        exist_ok=True)
            os.makedirs(os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, ROBO_WEB_CAM_COMPARATOR), mode=0o777,
                        exist_ok=True)
            robot_print_debug(f"Created Module dir as: {CommonKeywordsClass.TEST_MODULE_FOLDER}")
            os.environ["TEST_MODULE_FOLDER"] = CommonKeywordsClass.TEST_MODULE_FOLDER
        except Exception as exp:
            robot_print_error(f"Error to create the module folder name, EXCEPTION: {exp}")
            CommonKeywordsClass.TEST_MODULE_FOLDER = ""

    def get_logs_screenshot_path(self) -> str:
        """
        This method provide the path of actual image and used save the actual image. i.e. at the time of Opencv
        :return: <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot
        :exception: FileNotFoundError
        """
        try:
            path = os.path.join(os.environ["TEST_MODULE_FOLDER"], ROBO_LOGS_SCREENSHOT)
            if not os.path.isdir(path):
                raise IsADirectoryError(f"Given path '{path}' is not a directory")
            return path
        except KeyError as exp:
            robot_print_error(f"Logs path is not created due to 'TEST_MODULE_FOLDER; env variable not set,"
                              f"You need to call create_module_directory() method before getting Logs path"
                              f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Can not find the path of Logs and Screenshots, EXCEPTION: {exp}")

    def get_actual_image_folder_path(self) -> str:
        """
        This method provide the path of actual image and used save the actual image. i.e. at the time of Opencv
        :return: <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/ActualImages
        :exception: FileNotFoundError
        """
        try:
            path = os.path.join(os.environ["TEST_MODULE_FOLDER"], ROBO_ACTUAL_IMAGE)
            if not os.path.isdir(path):
                raise IsADirectoryError(f"Given path '{path}' is not a directory")
            return path
        except KeyError as exp:
            robot_print_error(f"Actual image path is not created due to 'TEST_MODULE_FOLDER; env variable not set,"
                              f"You need to call create_module_directory() method before getting actual image path"
                              f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Can not find the path of Logs and Screenshots, EXCEPTION: {exp}")

    def get_screenshot_path(self, test_name: str) -> str:
        """
        This method provide the screenshot path which test case id. User can use this method to save the screenshot.
        :param test_name: name for test case in which screenshot takes
        :return:
        <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot/<Test_case_id>/<screenshot_id>.png
        """
        try:
            # TODO: Change the name get_screenshot_name to get_screenshot_path
            test_name = test_name.split(" ")[0]
            dir_path = os.path.join(self.get_logs_screenshot_path(), test_name)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            screenshot_path = os.path.join(dir_path, f"{test_name}.png")
            return screenshot_path
        except Exception as exp:
            robot_print_error(f"Error to get the screenshot path, EXCEPTION: {exp}", print_in_report=True)

    def get_log_screenshot_directory(self, test_name: str) -> str:
        """
        This method is provide the path of logs and screenshot directory
        :param test_name: name of the test case which used to create the director
        :return:
        <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot/<testcaseid>
        """
        path = os.path.join(self.get_logs_screenshot_path(), test_name.split(" ")[0])
        try:
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
                robot_print_debug(f"Directory Created at path: {path}")
            return path
        except OSError as os_err:
            robot_print_error(f"There is an exception to create the module directory, EXCEPTION: %s" % os_err)
            return ""

    def get_test_case_id(self, test_name) -> str:
        """
        This method only provide the test case id from the teat case name
        :param test_name: name of the test case
        :return: test case id

        for eg. :  if Test case name is -> Req01 My Test case
                    then it return -> Req01
        """
        return test_name.split(" ")[0]

    def get_custom_ign_report_path(self, test_case_name) -> str:
        """
        This method provide the path for the ignition cycle logs.
        :return: <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/<testcaseid>/IgnitionLog
        """
        try:
            path = os.path.join(self.get_log_screenshot_directory(test_case_name), "IgnitionLog")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
                robot_print_debug(f"Path created: {path}")
            return path
        except Exception as exp:
            robot_print_error(f"Error to get the custom ign report path, EXCEPTION: {exp}",
                              print_in_report=True)

    def get_crash_log_path(self) -> str:
        """
        This method is create the performance logs path
        <root_path>/Test_Reports/Project_<date>_<time>/CrashLogsReport
        """
        try:
            path = os.path.join(self.get_report_path(), "CrashLogsReport")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
                print(f"Path created: {path}")
            sleep(5)
            return path
        except OSError as os_err:
            robot_print_error(f"There is an error to create crash logs directory, EXCEPTION: {os_err}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"Error at: {exc_type, fname, exc_tb.tb_lineno}")

    def __create_performance_path(self) -> str:
        """
        This method is create the performance logs path
        <root_path>/Test_Reports/Project_<date>_<time>/PerformanceUtilisation
        """
        try:
            path = os.path.join(self.get_report_path(), "PerformanceUtilisation")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
            sleep(5)
            return path
        except OSError as os_err:
            robot_print_error(f"There is an error to create Memory Utilisation directory,"
                              f" EXCEPTION: {os_err}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"Erorr at {exc_type, fname, exc_tb.tb_lineno}")

    def performance_utilization_custom_path(self, *args) -> str:
        """
        This method is used to create the Custom path.
        User can create the path under
        <home_path>/Test_Report/Project_<date>_<time>/PerformanceUtilisation/
        :param: *args: Multiple argument,
                       User can pass multiple String arguments to create the hierarchy of directories
        :except: OSError
        :arg: Multiple argument, User can pass multiple String arguments to
              create the hierarchy of directories
        :return: <home_path>/Test_Report/Project_<date>_<time>/PerformanceUtilisation/<custompath>
        """
        try:
            report_path = self.__create_performance_path()
            path = os.path.join(report_path, *args)
            if not os.path.isdir(path):
                os.makedirs(os.path.join(report_path, *args), mode=0o777)
            sleep(5)
            return str(path)
        except OSError as os_err:
            robot_print_error(f"There is an error to create Memory Utilisation directory, "
                              f"EXCEPTION: {os_err}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"Error at: {exc_type, fname, exc_tb.tb_lineno}")

    def get_can_trace_dir(self) -> str:
        """
        This method is used to create the CAN Trace path as
        <homepath>/<Project_<data>_<time>>/CAN_TRACE
        If path already exits the it not create the path simple return the path
        otherwise create the path.
        :return: CAN trace as <homepath>/<Project_<data>_<time>>/CAN_TRACE
        """
        try:
            can_trace = os.path.join(self.get_report_path(), "CAN_TRACE")
            if not os.path.isdir(can_trace):
                os.mkdir(can_trace, mode=0o777)
                sleep(1)
            return can_trace
        except OSError as os_err:
            robot_print_error(f"Error to create the CAN Trace dir, EXCEPTION :{os_err}")

    def get_vautocan_trace_dir(self) -> str:
        """
        This method is used to create the CAN Trace path as
        <homepath>/<Project_<data>_<time>>/Vauto_CAN_TRACE
        If path already exits the it not create the path simple return the path
        otherwise create the path.
        :return: CAN trace as <homepath>/<Project_<data>_<time>>/Vauto_CAN_TRACE
        """
        try:
            Vauto_CAN_TRACE = os.path.join(self.get_report_path(), "Vauto_CAN_TRACE")
            if not os.path.isdir(Vauto_CAN_TRACE):
                os.mkdir(Vauto_CAN_TRACE, mode=0o777)
                sleep(1)
            return Vauto_CAN_TRACE
        except OSError as os_err:
            robot_print_error(f"Error to create the CAN Trace dir, EXCEPTION :{os_err}")

    def create_system_log_directory(self) -> str:
        """
        This method is used to create the directory for module to save system logs
        :return: <root_path>/Test_reports/<project_folder_name>/<module_name>/SystemLogs
        """
        try:
            path = os.path.join(self.get_module_folder(), "SystemLogs")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
                print(f"Path created: {path}")
            return path
        except OSError as os_err:
            robot_print_error("There is an exception to create the module directory, EXCEPTION: %s" % os_err,
                              print_in_report=True)

    def get_adb_command_data_file_path(self) -> str:
        """
        This method provide the path for saving the adb commands output
        :return: <root_path>/Test_Reports/<project_folder_name>/Logs_Screenshot/ADB_Command_Data/
        """
        try:
            dir_path = os.path.join(self.get_logs_screenshot_path(), "ADB_Command_Data")
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, mode=0o777)
                robot_print_info(f"Path {dir_path} is created for saving ADB command data.")
            return dir_path
        except Exception as exp:
            robot_print_error(f"There is an error in get_adb_command_data_file_path(), EXCEPTION: {exp}")

    def create_adb_pull_file_path(self) -> bool:
        """
        This method is used to create the path to store the adb pull data.
        :return: True if directory created
        :rtype: Bool
        """
        try:
            path = os.path.join(self.get_report_path(), "AdbPullData")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
                return True
            return True
        except Exception as exp:
            robot_print_error(f"Error to create the path for storing adb pull data, EXCEPTION: {exp}",
                              print_in_report=True)

    def get_adb_pull_file_path(self) -> str:
        """
        This method is used to get the path for store the adb pull files
        :return: Path like string
        :rtype: String
        """
        try:
            if self.create_adb_pull_file_path():
                return os.path.join(self.get_report_path(), "AdbPullData")
        except Exception as exp:
            robot_print_error(f"Error to get the path for storing adb pull data, EXCEPTION: {exp}",
                              print_in_report=True)

    def __create_test_client_path(self) -> str:
        """
        This method is used to create the path for store the Python TestClient logs inside report
        :return: <reportpath>/TestClientLogs
        :rtype: String
        """
        try:
            dir_path = os.path.join(self.get_report_path(), "TestClientLogs")
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, mode=0o0777)
                robot_print_info(f"Path {dir_path} is created for saving Test client logs")
                return dir_path
        except Exception as exp:
            robot_print_error(f"Error to create the path of Test client logs, EXCEPTION: {exp}",
                              print_in_report=True)

    def get_test_client_log_path(self) -> str:
        """
        This method return the path of Test client logs.
        File name always be TestClientLog.log
        :return: <home_path>/Test_Report/Project_<date>_<time>/TestClientLogs/TestClientLog.log
        """
        path = self.__create_test_client_path()
        if path is not None:
            return os.path.join(path, "TestClientLog.log")

    def get_qfil_log_file_path(self) -> str:
        """
        This method create and return the path of QFIL logs directory.
        If path is not create it will create and return.
        :return: <homepath>/<reportpath>/QFILLogs/
        :rtype: Path like Object
        :exception: Handle Generic Exception, If there is an error it will return None
        """
        try:
            path = os.path.join(self.get_report_path(), "QFILLogs")
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)
            return path
        except Exception as exp:
            robot_print_error(f"Error to get the QFIL log file path, EXCEPTION: {exp}", print_in_report=True)
            return ""

    def get_path(self, name: str, parent: str = None, is_file: bool = False, is_dir: bool = True) -> Union[str, None]:
        """
        This function will return the requested path, It will check in depth path of root directory and return the path.
        User can request for either directory path or file path. But can not request for both.
        :param name: Path to be requested, either File or Directory
        :type name: String (Path like object)
        :param parent: Name of parent directory of given searching file or directory, If its None function will return
        firstly find directory or file.
        :type parent: String, default None.
        :param is_file: True if name is of File name otherwise True, Default False
        :type is_file: bool
        :param is_dir: True if name is of directory name otherwise True, Default True
        :type is_dir: bool
        :return: Path like string or None if path not found
        :rtype: Union[str, None]
        """
        try:
            if is_dir == is_file:
                raise ValueError("It seems you are looking for file and dir which is not possible. "
                                 "Please select either is_file=True or is_dir=True")
            flag = False
            if parent is None:
                flag = True
            for root, dires, files in os.walk(self.get_root_path()):
                if parent in dires:
                    flag = True
                if is_dir:
                    if root.split(os.sep)[-1] == name and flag and root.split(os.sep)[-2] == parent:
                        return root
                if is_file:
                    if name in files and flag:
                        return os.path.join(root, name)
            return None
        except Exception as exp:
            robot_print_error(f"Error to find the requested path: {name}, EXCEPTION: {exp}")
            return None

    def get_alexa_report_path(self):
        """
        This method provide the path of alexa report
        :exception: KeyError
        """
        try:
            return os.environ["ALEXA_REPORT_PATH"]
        except KeyError as key_err:
            robot_print_error(f"ALEXA_REPORT_PATH is not set as environment variable, EXCEPTION: {key_err}")

    def set_alexa_test_report_directory(self):
        """
       This method provide the path of newly creating report file. i.e Project_<date>_<time>
       :return: <home_path>/Test_Report/Project_<date>_<time>/<Alexa>
       """
        try:
            CommonKeywordsClass.TEST_MODULE_FOLDER = os.path.join(self.get_report_path(), "Alexa")
            if not os.path.isdir(CommonKeywordsClass.TEST_MODULE_FOLDER):
                os.makedirs(CommonKeywordsClass.TEST_MODULE_FOLDER, mode=0o777, exist_ok=True)
                return CommonKeywordsClass.TEST_MODULE_FOLDER
        except Exception as exp:
            robot_print_error(f"Error to create the folder, EXCEPTION: {exp}", print_in_report=True)
            return ""

    def get_alexa_output_command_dir_path(self):
        """
        The method will save the speech audio in output directory.
        e.g. CRE/SWE5_SWIntegrationTest/Test_Reports/Alexa/Reports/Output_Command/element.mp3
        :return: it will return path
        """
        try:
            self.set_alexa_test_report_directory()
            PATH_MODULE = os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports", "Output_Command")
            if not os.path.isdir(PATH_MODULE):
                os.makedirs(PATH_MODULE, mode=0o777)
                robot_print_debug(f"Created Module dir as: {CommonKeywordsClass.TEST_MODULE_FOLDER}")
            return PATH_MODULE
        except Exception as exp:
            robot_print_error(f"Error to create the module folder name, EXCEPTION: {exp}")

    def output_command_dir_path(self):
        """
        This method provide the path of alexa report
        :exception: KeyError
        """
        try:
            return os.environ["ALEXA_OP_PATH"]
        except KeyError as key_err:
            robot_print_error(f"ALEXA_OP_PATH is not set as environment variable, EXCEPTION: {key_err}")

    def get_alexa_report_input_command_path(self, unique_key):
        """
        The method will save the speech audio in output directory.
        e.g. CRE/SWE5_SWIntegrationTest/Test_Reports/Alexa/Reports/Input_Command/element.mp3
        :param unique_key :command to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc.
        :return: it will return path
        """
        try:
            self.set_alexa_test_report_directory()
            os.makedirs(
                os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports", "Input_Command"),
                mode=0o777,
                exist_ok=True)
            return os.path.join(
                os.path.join(CommonKeywordsClass.TEST_MODULE_FOLDER, "Reports", "Input_Command", f"{unique_key}.mp3"))
        except Exception as exp:
            robot_print_error(f"Error to create the module folder name, EXCEPTION: {exp}")

    def get_image_screenshot_path(self):
        """
        This function takes the Reports path and creates the IMAGE folder if not exists, if present returns the IMAGE path
        """
        try:
            image_path = os.path.join(self.get_report_path(), "IMAGE")
            if not os.path.isdir(image_path):
                os.mkdir(image_path, mode=0o777)
                sleep(1)
            return image_path
        except OSError as os_err:
            robot_print_error(f"Error to create the IMAGE dir, EXCEPTION :{os_err}")

    def get_robot_xml_report_path(self):
        try:
            path = os.path.join(self.get_report_path(), ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_XML_FILE_NAME)
            if os.path.isfile(path):
                return path
            return None
        except Exception as exp:
            robot_print_error(f"Error to get the robot xml report path, EXCEPTION: {exp}")
            return None

    def get_robot_html_report_path(self):
        try:
            path = os.path.join(self.get_report_path(), ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_HTML_FILE_NAME)
            if os.path.isfile(path):
                return path
            return None
        except Exception as exp:
            robot_print_error(f"Error to get the robot html report path, EXCEPTION: {exp}")
            return None

    def get_robot_html_log_path(self):
        try:
            path = os.path.join(self.get_report_path(), ROBOT_REPORT_FOLDER_NAME, ROBOT_LOG_HTML_FILE_NAME)
            if os.path.isfile(path):
                return path
            return None
        except Exception as exp:
            robot_print_error(f"Error to get the robot html log path, EXCEPTION: {exp}")
            return None

    def get_input_files_dir_path(self):
        """
        This function is used to get the <path>/ExternalFiles/InputFiles directory path
        :return: Path of <path>/ExternalFiles/InputFiles.
            if a user is using old CRE structure then path will be: CRE/Libraries/ExternalFiles/InputFiles
            if a user is using new CRE structure then path will be: CRE/ExternalFiles/InputFiles

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_EXTERNAL_FILES, CRE_INPUT_FILES)
        else:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_dbc_dir_path(self):
        """
          This function is used to get the <path>/ExternalFiles/DbFiles directory path
          :return: Path of <path>/ExternalFiles/DbFiles
              if a user is using old CRE structure then path will be: CRE/Libraries/ExternalFiles/DbFiles
              if a user is using new CRE structure then path will be: CRE/ExternalFiles/DbFiles

              This function will handle old and new structure internally. User doesn't need to take care of this.
          :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_EXTERNAL_FILES, CRE_DB_FILES)
        else:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_DB_FILES)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_build_dir_path(self):
        """
        This function is used to get the <path>/ExternalFiles/InputFiles/Build directory path
        :return: Path of <path>/ExternalFiles/InputFiles/Build
            if a user is using old CRE structure then path will be: CRE/Libraries/ExternalFiles/InputFiles/Build
            if a user is using new CRE structure then path will be: CRE/ExternalFiles/InputFiles/Build

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_input_files_dir_path(), CRE_INPUT_BUILD_DIR)
        else:
            dir_path = os.path.join(self.get_input_files_dir_path(), CRE_INPUT_BUILD_DIR)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_resource_dir_path(self):
        """
        This function is used to get the <path>/Resources directory path
        :return: Path of <path>/Resources
            if a user is using old CRE structure then path will be: CRE/Libraries/Resources
            if a user is using new CRE structure then path will be: CRE/Resources

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_RESOURCES)
        else:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_LIBRARIES, CRE_RESOURCES)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_test_scripts_path(self):
        """
           This function is used to get the Robot Scripts directory path
           :return: Path of Robot Script
               if a user is using old CRE structure then path will be: CRE/SWE5_SWIntegrationTest/ProjectTests
               if a user is using new CRE structure then path will be: CRE/RobotScripts

               This function will handle old and new structure internally. User doesn't need to take care of this.
           :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_root_path(), PROJECT, ROBOT_SCRIPTS, TEST_CASES_SCRIPTS)
        else:
            dir_path = os.path.join(self.get_root_path(), PROJECT, self.team_name, TEST_CASES)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_build_info_txt_file_path(self):
        """
        This function is used to get the ExternalFiles/InputFiles/BuildInfo.txt directory path
        :return: Path of ExternalFiles/InputFiles/BuildInfo.txt
            if a user is using old CRE structure then path will be: CRE/Libraries/ExternalFiles/InputFiles/BuildInfo.txt
            if a user is using new CRE structure then path will be: CRE/ExternalFiles/InputFiles/BuildInfo.txt

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            file_path = os.path.join(self.get_input_files_dir_path(), CRE_BUILD_INFO_FILE)
        else:
            file_path = os.path.join(self.get_input_files_dir_path(), CRE_BUILD_INFO_FILE)
        if os.path.isfile(file_path):
            return file_path
        robot_print_error(f"Invalid directory path '{file_path}'")
        raise FileNotFoundError(f"BuildInfo.txt file is not found at '{file_path}'")

    def get_project_keywords_dir_path(self):
        """
        This function is used to get the ProjectKeywords/project_keyword.py directory path
        :return: Path of ProjectKeywords/project_keyword.py
            if a user is using old CRE structure then path will be: CRE/Libraries/ProjectKeywords/project_keyword.py
            if a user is using new CRE structure then path will be: CRE/ProjectKeywords/project_keyword.py

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        if self.team_name == TEAM_ROBOT_SCRIPT:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_PROJECT_KEYWORDS)
        else:
            dir_path = os.path.join(self.get_root_path(), PROJECT, CRE_LIBRARIES, CRE_PROJECT_KEYWORDS)
        if os.path.isdir(dir_path):
            return dir_path
        robot_print_error(f"Invalid directory path '{dir_path}'")
        raise NotADirectoryError(f"Given '{dir_path}' is invalid.")

    def get_robot_json_report_path(self):
        """
        This function is used to get the xray json file directory path
        :return: <report_path>/Reports/xray_json_file.json
        :rtype: Path Like String
        """
        try:
            path = os.path.join(self.get_report_path(), ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_JSON_FILE_NAME)
            return path
        except Exception as exp:
            robot_print_error(f"Error to get the robot xml report path, EXCEPTION: {exp}")
            return None

    @property
    def build_number(self):
        """
        This function is getter function and return the value of build number
        :return: Build number
        :rtype: String
        """
        with open(self.get_build_info_txt_file_path(), mode="r") as fp:
            build_number = fp.readline().strip()
        return build_number

    def get_user_name(self):
        print("get root path:")
        return self.get_root_path().strip().split("/")[2]

    def get_ufs_allocation_file(self):
        f"""
        This function is used to get the <path>ExternalFiles/InputFiles directory path
        :return: Path of  <path>ExternalFiles/InputFiles/{UFS_ALLOCATION_FILE}
            if a user is using old CRE structure then path will be: CRE/Libraries/ExternalFiles/InputFiles/{UFS_ALLOCATION_FILE}
            if a user is using new CRE structure then path will be: CRE/ExternalFiles/InputFiles/{UFS_ALLOCATION_FILE}

            This function will handle old and new structure internally. User doesn't need to take care of this.
        :rtype: Path Like String
        """
        try:
            file_path = os.path.join(self.get_input_files_dir_path(), UFS_ALLOCATION_FILE)
            if os.path.isfile(file_path):
                return file_path
        except Exception as exp:
            robot_print_error(f"Error to get the robot xml report path, EXCEPTION: {exp}")
            return None

    def get_webcam_image_path(self, test_name: str) -> str:
        """
        This method provide the screenshot path which test case id. User can use this method to save the screenshot.
        :param test_name: name for test case in which screenshot takes
        :return:
        <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot/<Test_case_id>/<screenshot_id>.png
        """
        try:
            test_name = test_name.split(" ")[0]
            dir_path = os.path.join(self.get_web_cam_path(), test_name)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            screenshot_path = os.path.join(dir_path, f"{test_name}.png")
            return screenshot_path
        except Exception as exp:
            robot_print_error(f"Error to get the screenshot path, EXCEPTION: {exp}", print_in_report=True)

    def get_web_cam_path(self) -> str:
        """
           Provides the path for storing actual images, used during OpenCV operations.
           Returns:
               str: Path in the format: <home_path>/Test_Report/Project_<date>_<time>/<Module_Name>/Logs_Screenshot
           Raises:
               IsADirectoryError: If the given path is not a directory.
               KeyError: If 'TEST_MODULE_FOLDER' environment variable is not set.
               Exception: If there is an error finding the path of Logs and Screenshots.
        """

        try:
            path = os.path.join(os.environ["TEST_MODULE_FOLDER"], ROBO_WEB_CAM_COMPARATOR)
            if not os.path.isdir(path):
                raise IsADirectoryError(f"Given path '{path}' is not a directory")
            return path
        except KeyError as exp:
            robot_print_error(f"Logs path is not created due to 'TEST_MODULE_FOLDER; env variable not set,"
                              f"You need to call create_module_directory() method before getting Logs path"
                              f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Can not find the path of Logs and Screenshots, EXCEPTION: {exp}")

    def get_audio_verification_wav_files_path(self):
        try:
            path = os.path.join(self.get_logs_screenshot_path(), "AudioAnalysis")
            if not os.path.isdir(path):
                os.makedirs(path)
            return path
        except OSError as exp:
            robot_print_error(f"Error to create or get the path of wave file, EXCEPTION: {exp}")