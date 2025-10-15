from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectKeywordFile import ProjectKeywordFile
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.BuildDownload.DownloadAuto import DownloadAuto
from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.UserXmlReporting import UserXmlReporting
import time
from Robo_FIT.GenericLibraries.GenericOpLibs.GrafanaDashboard.GrafanaDashboardData import GrafanaDashboardData
from importlib import import_module
import os
import re
import shutil
import sys
import argparse
from pathlib import Path


# from importlib import import_module


class ExecutionClass:
    VALID_TEAM_NAME = {"1": "swe4", "2": "swe5", "3": "swe6", "4": "sys4", "5": "sys5", "6": "RobotScripts"}
    VALID_CHOICE = ["True", "true", "False", "false"]

    def __init__(self, root_path, team_name):
        try:
            self.helper = CommonKeywordsClass()
            self.helper.set_root_directory(root_path)
            self.helper.check_team_name(team_name)
            self.project_manager = ProjectConfigManager()
            # Create the keyword file
            ProjectKeywordFile()
        except FileNotFoundError as exp:
            robot_print_error(f"Exception {exp}", print_in_report=True)
            sys.exit(-1)
        except OSError as exp:
            robot_print_error(f"Exception {exp}", print_in_report=True)
            sys.exit(-1)

    def call_project_build_download_func(self, build_variant: str = None, pick_for_date: str = "latest"):
        project_class_name = ''
        try:
            if build_variant is not None:
                download_auto = DownloadAuto()
                download_auto.download_build(variant_value=build_variant, build_param=pick_for_date)
            #     project_class_name = self.project_manager.get_project_handler_class()
            #     if project_class_name != '':
            #         module = import_module(f"CRE.Libraries.ProjectLibs.Project.{project_class_name}")
            #         project_class = getattr(module, project_class_name)()
            #         project_class.download_build(build_variant=build_variant)
        except ModuleNotFoundError as exp:
            robot_print_error(f"Module {project_class_name} is not found under CRE.Libraries.ProjectLibs.Project, "
                              f"EXCEPTION: {exp} ")
        except NotImplementedError as exp:
            robot_print_error(f"download_build(build_variant=None) function is not implemented by project, "
                              f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Error to download the build, EXCEPTION {exp}")
            sys.exit(f"{exp}")

    def execute_robot(self, tags_list=None, check_report=False, test_execution_key=None, test_plan_key=None,
                      test_sub_group=None, test_group=None,
                      test_type_name=None, is_upload_execution_record=True, build_variant=None, build_date='latest'):
        date_time = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")

        project = self.project_manager.get_project_name()
        final_tag_list = []
        if tags_list is None:
            final_tag_list = self.get_tag_list()
        else:
            final_tag_list = tags_list
        """
        Due to global CICD changes we are not adding SW name in Report Folder Name
        # build = self.get_build_info()
        # 
        # if build is not None:
        #     folder_name = project + "_SW" + build + "_" + date_time
        # else:
        #     folder_name = project + "_" + date_time
        """
        folder_name = project + "_" + date_time
        try:
            report_path = self.helper.create_report_path(team_name=self.helper.team_name, report_name=folder_name)
            os.makedirs(os.path.join(report_path, "Reports"), mode=0o777)
            self.call_project_build_download_func(build_variant=build_variant, pick_for_date=build_date)
            self.commands_execution(report_path, self.helper.team_name, final_tag_list)
            self.collect_TestArtifacts()
            time.sleep(5)
            custom_report_path = os.path.join(report_path, "CustomReport.html")
            if os.path.isfile(custom_report_path):
                os.system("start {path}".format(path=custom_report_path))
            if check_report:
                self.check_final_status()

            # upload to grafana based on the user configuration
            is_upload_record_on_grafana = self.project_manager.is_upload_record_to_grafana()
            if is_upload_record_on_grafana:
                upload_grafana_data = GrafanaDashboardData()
                if self.find_performance_excel_file():
                    robot_print_info(f"Grafana upload started", print_in_report=True, underline=True)
                    upload_grafana_data.upload_data()
                else:
                    robot_print_error(f"No performance excel sheets generated", print_in_report=True, underline=True)

            # upload the report base on the user configuration
            # "isImportExecutionRecord": true,
            if is_upload_execution_record:
                from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.XrayExecutionRecordUpload import \
                    XrayExecutionRecordUpload
                robot_print_info(f"User has started the execution with uploading the test execution record",
                                 print_in_report=True, underline=True)
                xray_upload = XrayExecutionRecordUpload()
                # xray_upload.upload_execution_record()
                xray_upload.start_upload_xray_record_by_json(test_execution_key=test_execution_key,
                                                             test_plan_key=test_plan_key, test_sub_group=test_sub_group,
                                                             test_group=test_group, test_type=test_type_name,
                                                             build_version=self.get_build_info())
                xray_upload.jira_report_upload()

            else:
                robot_print_info(f"User has started the execution without uploading the test execution record",
                                 print_in_report=True, underline=True)

        except Exception as exp:
            robot_print_error(f"Error while executing {exp}", print_in_report=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}", print_in_report=True)

    def upload_only_execution_record(self, test_execution_key=None, test_plan_key=None, test_group_name=None,
                                     test_group=None, test_type_name=None, is_upload_execution_record=True,
                                     test_report_path=None):
        if is_upload_execution_record:
            from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.XrayExecutionRecordUpload import \
                XrayExecutionRecordUpload
            robot_print_info(f"User has started the upload of the test execution record without execution",
                             print_in_report=True, underline=True)
            xray_upload = XrayExecutionRecordUpload()
            xray_upload.start_upload_xray_record_by_json(test_execution_key=test_execution_key,
                                                         test_plan_key=test_plan_key, test_sub_group=test_group_name,
                                                         test_group=test_group, test_type=test_type_name,
                                                         build_version=self.get_build_info(),
                                                         test_report_path=test_report_path)
            xray_upload.jira_report_upload(test_report_path=test_report_path)
        else:
            robot_print_error(f"Error to upload the test execution record without execution", print_in_report=True,
                              underline=True)

    def find_performance_excel_file(self):
        try:
            self.boot_kpi_excel_file = os.path.join(self.helper.get_report_path(), PERFORMANCE_UTILISATION_DIR,
                                                    ROBO_BOOT_KPI_DIR_NAME, ROBO_BOOT_KPI_EXCEL_NAME)
            if os.path.exists(self.boot_kpi_excel_file):
                return self.boot_kpi_excel_file, 'Sheet'
            else:
                robot_print_info(f"No excel file found. Please check documentation for generating performance log excel",
                                 print_in_report=True, underline=True)
                return None
        except Exception as e:
            robot_print_error(f"Error to get performance excel, EXCEPTION: {e}")

    def get_build_info(self) -> str:
        """
        This method gets build information from Hardware
        Varies according to different projects
        :return:
        """
        build_info = ""
        try:
            file_name = self.helper.get_build_info_txt_file_path()
            robot_print_debug(f"Build info file path: {file_name}", print_in_report=True)
            with open(file_name, mode="r") as fp:
                line = fp.readline()
                while line:
                    build_info = line
                    line = fp.readline()
                fp.close()
            user_xml = UserXmlReporting()
            user_xml.read_build_info(build_info)
            robot_print_info(f"Testing Build: {build_info}", print_in_report=True)
            if "\n" in build_info:
                build_info = build_info.replace('\n', '')
            return build_info.strip()
        except Exception as exp:
            robot_print_error(f"Error to get the build info from the file, EXCEPTION: {exp}")
            return build_info

    def get_tag_list(self) -> list:
        """
        This methods gives tag list from Configuration File
        :return:
        """
        tags_list = self.project_manager.get_tag_list()
        if tags_list is not None:
            return tags_list.strip().split(" ")
        else:
            raise Exception("Error getting Tags list!!! Please check Project Configuration File")

    def commands_execution(self, report_path, team, tag_list):
        tag_string = ""
        robot_print_info(f"Executing tags: {tag_list}")
        for i in range(0, len(tag_list)):
            tag_string = tag_string + "-i" + " " + tag_list[i] + " "
        test_output_dir = os.path.join(report_path, "Reports")

        testcases_path = self.helper.get_test_scripts_path()
        robot_print_debug(f"Test case path: {testcases_path}")

        if not os.path.isdir(testcases_path):
            print_error(f"Test cases directory does not exists, Path: {testcases_path}", underline=True)
            sys.exit("Test cases directory does not exists")
        if sys.platform.startswith("linux"):
            robot_cmd = "python3 -m robot"
        elif sys.platform.startswith("win32"):
            robot_cmd = "robot"
        else:
            raise Exception("Unsupported OS, Please use only supported OS.")

        os.system(
            "{robot_cmd} -b {logfile} {tag_string} -l {path}/test_log.html -r {path}/test_report.html -o {path}/test_output.xml "
            "{testcase}".format(robot_cmd=robot_cmd, logfile=os.path.join(report_path, "RobotLogs.log"),
                                testcase=testcases_path,
                                tag_string=tag_string, path=test_output_dir))
        robot_print_debug(f"Execution Complete")

    def collect_TestArtifacts(self):
        """
        :return:
        """
        try:
            robot_print_debug(f"Collection Test Artifacts", print_in_report=True)
            dir_name = os.getcwd()
            test = os.listdir(dir_name)
            for item in test:
                if item.endswith(".txt"):
                    os.remove(os.path.join(dir_name, item))

            if os.path.isfile(os.path.join(self.helper.get_root_path(), ROBO_UDS_ON_CAN_LOG_FILE)):
                shutil.copy(os.path.join(self.helper.get_root_path(), ROBO_UDS_ON_CAN_LOG_FILE),
                            self.helper.get_can_trace_dir())
                robot_print_debug(
                    f"Move Done of file : {os.path.join(self.helper.get_root_path(), ROBO_UDS_ON_CAN_LOG_FILE)} "
                    f"to {self.helper.get_can_trace_dir()}")
            for file in os.listdir(self.helper.get_root_path()):
                if "robofit_log" in file:
                    shutil.copy(os.path.join(self.helper.get_root_path(), file),
                                os.path.join(self.helper.get_report_path()))

        except IOError as io:
            robot_print_error(f"File report.txt does not exist: {io}", print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to collect the Test Artifacts, EXCEPTION: {exp}")

    def check_final_status(self):
        try:
            from lxml import etree
            report_path = os.path.join(self.helper.get_report_path(), "Reports", "test_output.xml")
            robot_print_debug(f"report_path is :{report_path}")
            if os.path.isfile(report_path):
                robot_print_debug(f"Checking the report......")
                root = etree.parse(report_path)
                for result in root.findall("statistics"):
                    for total in result:
                        for stat in total:
                            if stat.text == "All Tests":
                                robot_print_info(f"PASS TEST COUNT IS : {stat.attrib['pass']}")
                                robot_print_info(f"FAIL TEST COUNT IS : {stat.attrib['fail']}")
                                if stat.attrib['fail'] != "0":
                                    sys.exit(-1)
                                break
        except Exception as exp:
            robot_print_error(f"Error to check the final report status, EXCEPTION: {exp}")

    def call_project_build_download_func(self, build_variant: str = None, pick_for_date: str = "latest"):
        project_class_name = ''
        try:
            if build_variant is not None:
                download_auto = DownloadAuto()
                download_auto.download_build(variant_value=build_variant, build_param=pick_for_date)
            #     project_class_name = self.project_manager.get_project_handler_class()
            #     if project_class_name != '':
            #         module = import_module(f"CRE.Libraries.ProjectLibs.Project.{project_class_name}")
            #         project_class = getattr(module, project_class_name)()
            #         project_class.download_build(build_variant=build_variant)
        except ModuleNotFoundError as exp:
            robot_print_error(f"Module {project_class_name} is not found under CRE.Libraries.ProjectLibs.Project, "
                              f"EXCEPTION: {exp} ")
        except NotImplementedError as exp:
            robot_print_error(f"download_build(build_variant=None) function is not implemented by project, "
                              f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"Error to download the build, EXCEPTION {exp}")
            sys.exit(f"{exp}")


if __name__ == '__main__':
    # print(os.path.dirname(os.path.dirname(__file__)))
    # print(os.path.abspath('.').split(os.sep))
    arguments = sys.argv
    print(f"Arguments: {arguments}")


    def main():
        parser = argparse.ArgumentParser(
            prog="python ExecutionClass.py",
            description="Run RoboFIT scripts"
        )
        parser.add_argument(
            "-v",
            "--build-variant",
            nargs="?",
            dest="build",
            help="download the build",
            required=False
        )
        parser.add_argument(
            "-d",
            "--build-param",
            dest="build_param",
            help="Please provide the url of the build or date of the build which the user wants to download. "
                 "The format of the date should be 'DD-MM-YYYY'. For ex. 19-Sep-2023. "
                 "If user wants to download the latest build, please use value as 'latest'.",
            required=False,
            default="latest"
        )
        parser.add_argument(
            "-p",
            "--current-path",
            nargs="?",
            dest="path",
            help="Current path of the execution ",
        )

        parser.add_argument(
            "-t",
            "--team",
            dest="team",
            help=f"Name of the Team, valid options can be {ExecutionClass.VALID_TEAM_NAME}",
            # choices=ExecutionClass.VALID_TEAM_NAME,
            required=True
        )
        parser.add_argument(
            "-rp",
            "--report-folder",
            dest="report_folder",
            help="Report folder name that user wants to upload the execution for",
            required=False
        )
        parser.add_argument(
            "-op",
            "--execution-option",
            dest="execution_option",
            help=f"Pass the value if the user wants to start the new execution or only upload the record, Options can "
                 f"be: {EXECUTION_OPTIONS}",
            default=1,
            required=False
        )
        parser.add_argument(
            "-u",
            "--upload-execution-record",
            dest="isUploadExecutionRecord",
            help="pass values as 'Yes' if user wants to upload the test execution record",
            required=True,
            default="Yes"
        )
        parser.add_argument(
            "-m",
            "--make-can-excel",
            dest="make",
            help="Make the CAN input excel file",
            required=False
        )
        parser.add_argument(
            "-i",
            "--crop-image-save-template",
            dest="crop",
            help="Crop and save the template Image",
            required=False
        )
        parser.add_argument(
            "-T",
            "--tags",
            dest="tags",
            help="Add the tags",
            required=False
        )
        parser.add_argument(
            "-c",
            "--check_result",
            dest="check_result",
            help="you want to check status, either pass True or False",
            choices=ExecutionClass.VALID_CHOICE,
            required=False
        )
        parser.add_argument(
            "-tkey",
            "--test-execution-key",
            dest="test_execution_key",
            help="Test Execution key, "
                 "if user want to create new test case then pass value as NEW otherwise JIRA Test Execution Key",
            required=False
        )
        parser.add_argument(
            "-tplankey",
            "--test-plan-key",
            dest="test_plan_key",
            help="Test Execution plan key with user want to link the test execution",
            required=False
        )
        parser.add_argument(
            "-tgrouptype",
            "--test-group-type",
            dest="test_group_type",
            help=f"Test Group option type, Options can be: {TEST_GROUPS}",
            required=False
        )
        parser.add_argument(
            "-tgroup",
            "--test-group-value",
            dest="test_group",
            help=f"Test Group option value, Options can be: {TEST_SUB_GROUPS}",
            required=False
        )
        parser.add_argument(
            "-ttype",
            "--test-type-value",
            dest="test_type",
            help=f"Test Type option value, Options can be: {TEST_CASE_TYPES}",
            required=False
        )
        result = parser.parse_args()
        print(result)

        def check_user_choice():
            if result.check_result == "True" or result.check_result == "true":
                return True
            elif result.check_result == "False" or result.check_result == "false":
                return False

        def check_is_valid_team_name():
            if result.team in ExecutionClass.VALID_TEAM_NAME.keys():
                return True
            return False

        def folder_path_exists(folder_path):
            path_pattern = r'^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
            if re.match(path_pattern, folder_path):
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    return True
            return False

        def check_execution_options(passed_value):
            for key, option in EXECUTION_OPTIONS.items():
                if key == passed_value:
                    robot_print_info(f"User has provided the test group as: {option}")
                    return option
            sys.exit(f"Please provide valid value of Test Group, Valid options are: {EXECUTION_OPTIONS}")

        def check_is_execution_key_provided(passed_value):
            if passed_value.upper() == "NEW":
                return None
            else:
                robot_print_info(f"User has provided the execution key as: {passed_value}")
                return passed_value

        def check_test_group_value(value):
            for key, test_group in TEST_SUB_GROUPS.items():
                if key == value:
                    robot_print_info(f"User has provided the test group as: {test_group}")
                    return test_group
            sys.exit(f"Please provide valid value of Test Group, Valid options are: {TEST_SUB_GROUPS}")

        def check_test_group_type(value):
            for key, test_group in TEST_GROUPS.items():
                if key == value:
                    robot_print_info(f"User has provided the test group as: {test_group}")
                    return test_group
            sys.exit(f"Please provide valid value of Test Group, Valid options are: {TEST_SUB_GROUPS}")

        def check_test_type_value(value):
            for key, test_type in TEST_CASE_TYPES.items():
                if key == value:
                    robot_print_info(f"User has provided the test type as: {test_type}")
                    return test_type
            sys.exit(f"Please provide valid value of Test Type, Valid value are: {TEST_CASE_TYPES}")

        def check_test_plan_key(value):
            if value is None:
                sys.exit(f"Invalid Test Plan Key: {value}, Please check and run again")
            if value == "":
                sys.exit(f"Invalid Test Plan Key: {value}, Please check and run again")
            else:
                return value

        def validate_build_param(build_param:str):
            if build_param is None:
                return True
            try:
                date_time_param = datetime.strptime(build_param, "%d-%b-%Y")
                return True
            except ValueError:
                if build_param.startswith("http"):
                    return True
                elif build_param.startswith("latest"):
                    return True
                else:
                    raise ValueError(f"Given build param '{build_param}' is not valid param.")

        def run_execution_with_upload_records(execution_class: ExecutionClass, tags_list):
            execution_class.execute_robot(tags_list=tags_list, check_report=check_user_choice(),
                                          test_execution_key=check_is_execution_key_provided(result.test_execution_key),
                                          test_plan_key=check_test_plan_key(result.test_plan_key),
                                          test_sub_group=check_test_group_value(result.test_group),
                                          test_group=check_test_group_type(result.test_group_type),
                                          test_type_name=check_test_type_value(result.test_type),
                                          is_upload_execution_record=True, build_variant=result.build,
                                          build_date=result.build_param)

        def run_execution_with_not_upload_records(execution_class: ExecutionClass, tags_list):
            execution_class.execute_robot(tags_list=tags_list, check_report=check_user_choice(),
                                          test_execution_key=None,
                                          test_plan_key=None,
                                          test_sub_group=None,
                                          test_group=None,
                                          test_type_name=None,
                                          is_upload_execution_record=False, build_variant=result.build,
                                          build_date=result.build_param)

        def upload_record_without_execution(execution_class, report_path):
            execution_class.upload_only_execution_record(
                test_execution_key=check_is_execution_key_provided(result.test_execution_key),
                test_plan_key=check_test_plan_key(result.test_plan_key),
                test_group_name=check_test_group_value(result.test_group),
                test_group=check_test_group_type(result.test_group_type),
                test_type_name=check_test_type_value(result.test_type),
                is_upload_execution_record=True, test_report_path=report_path)

        try:
            is_valid_team_name = check_is_valid_team_name()
            execution_path = Path(result.path).parent
            print(f"Execution Path: {Path(result.path).parent}")
            if int(result.execution_option) == 1:
                if not validate_build_param(result.build_param):
                    # if invalid build param then close the program
                    sys.exit(-1)
                if is_valid_team_name:
                    if result.tags is not None:
                        print(result.check_result)
                        execution = ExecutionClass(execution_path, ExecutionClass.VALID_TEAM_NAME[result.team])
                        if result.isUploadExecutionRecord.upper() == "Yes".upper():
                            run_execution_with_upload_records(execution_class=execution,
                                                              tags_list=result.tags.split(","))
                        elif result.isUploadExecutionRecord.upper() == "No".upper():
                            run_execution_with_not_upload_records(execution_class=execution,
                                                                  tags_list=result.tags.split(","))
                    elif result.make:
                        from Robo_FIT.GenericLibraries.GenericOpLibs.ControllerAreaNetwork.MakeCANInputData.MakeCanInputData import \
                            MakeCanInputData
                        data = MakeCanInputData(execution_path)
                        data.make_can_input_data()

                    elif result.crop:
                        from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.ImageFinder import ImageFinder
                        imagecrop = ImageFinder()
                        imagecrop.input_data()

                    elif result.isUploadExecutionRecord.upper() == "Yes".upper():
                        robot_custom_print(f"User want to upload the record = {result.isUploadExecutionRecord}",
                                           print_in_report=True, underline=True, color="dark_cyan")
                        execution = ExecutionClass(execution_path, ExecutionClass.VALID_TEAM_NAME[result.team])
                        run_execution_with_upload_records(execution_class=execution, tags_list=None)

                    elif result.isUploadExecutionRecord.upper() == "No".upper():
                        robot_custom_print(f"User want to upload the record = {result.isUploadExecutionRecord}",
                                           print_in_report=True, underline=True, color="dark_cyan")
                        execution = ExecutionClass(execution_path, ExecutionClass.VALID_TEAM_NAME[result.team])
                        run_execution_with_not_upload_records(execution_class=execution, tags_list=None)
                else:
                    raise ValueError(
                        f"Invalid team name provided by the user, please provide valid team. "
                        f"VALID VALUES are: {ExecutionClass.VALID_TEAM_NAME}")
            elif int(result.execution_option) == 2:
                robot_print_info(f"entered 2 option")
                is_valid_team_name = check_is_valid_team_name()
                execution_path = Path(result.path).parent
                if not validate_build_param(result.build_param):
                    # if invalid build param then close the program
                    sys.exit(-1)
                if is_valid_team_name:
                    if not folder_path_exists(result.report_folder):
                        report_path = os.path.join(execution_path, PROJECT, TEAM_SWE5, TEST_REPORTS, result.report_folder)
                    else:
                        report_path = result.report_folder
                    robot_print_info(f"robot report path: {report_path}")
                    if folder_path_exists(report_path):
                        robot_print_debug(f"path exists")
                        execution = ExecutionClass(execution_path, ExecutionClass.VALID_TEAM_NAME[result.team])
                        upload_record_without_execution(execution_class=execution, report_path=report_path)
                    else:
                        robot_print_error(f"Folder path provided doesn't exists")
                else:
                    raise ValueError(
                        f"Invalid team name provided by the user, please provide valid team. VALID VALUES "
                        f"are: {ExecutionClass.VALID_TEAM_NAME}")
            else:
                raise ValueError(
                    f"Invalid option provided by the user, please enter valid option. VALID VALUES are: "
                    f"{EXECUTION_OPTIONS}, Provided option are:{result.execution_option}")
        except ValueError as exp:
            robot_print_error(f"Error to execute the robotfit scripts: {exp}")


    main()
