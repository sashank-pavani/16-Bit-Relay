import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import List, Tuple, Union, Dict

from bs4 import BeautifulSoup
from jsonschema import validate
from jsonschema.exceptions import SchemaError

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ROBO_FIT, ROBO_LIBS, ROBO_COMPONENTS, \
    XRAY_UTILITY_MODULE, ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_XML_FILE_NAME, ROBOT_REPORT_JSON_FILE_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.JiraApiHandler import JiraApiHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.TcUpload.ConvertRobotToExcel import ConvertRobotToExcel


class ConvertXmlToJson:
    # Test Execution Custom Fields
    __test_execution_custom_fields_name = ["Test Group", "Test Case Type"]

    def __init__(self, test_plan_key: str = None, existing_test_exec: str = None,
                 test_sub_group: str = None, test_group: str = None, test_type: str = None, test_report_path=None):
        """
        Constructor of CovertXmlToJson class
        :param test_plan_key: Jira Test Plan key, which user wants to link the test execution
        :type test_plan_key: String
        :param existing_test_exec: Jira Test Execution key if you want to update any existing test execution
        :type existing_test_exec: String
        :param test_sub_group: Test Group Name, which user wants to assign to all the executed test case's
        :type test_sub_group: String
        :param test_type: Test Case Type, which user want to assign to all the executed test case's
        :type test_type: String
        """
        self.project_manager = ProjectConfigManager()
        self.common_keyword = CommonKeywordsClass()
        if test_report_path:
            self.xml_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_XML_FILE_NAME)
            self.json_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME, ROBOT_REPORT_JSON_FILE_NAME)
        else:
            self.xml_file_path = self.common_keyword.get_robot_xml_report_path()
            self.json_file_path = self.common_keyword.get_robot_json_report_path()
        self.report_data = None
        self.fina_record = {}
        self.test_objs = []
        self.test_plan_key = test_plan_key
        self.existing_test_exce = existing_test_exec
        self.__read_xml_file()
        self.test_summary_list = []
        self.test_id_list = []
        self.test_sub_group = test_sub_group
        self.test_group = test_group
        self.test_type = test_type
        self.df = None
        self.converter = ConvertRobotToExcel()

        # project key
        self.project_key = self.project_manager.get_project_test_execution_key()

        # jira api
        self.jira_api_handler = JiraApiHandler()

        # logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def __read_xml_file(self):
        """
        Read the robot xml file
        :return: Object of BeautifulSoup
        :rtype: Object
        :raise: FileNotFoundError if robot xml file not found
        """
        if self.xml_file_path is not None:
            if self.report_data is None:
                self.report_data = BeautifulSoup(open(self.xml_file_path, "r", encoding="utf-8"), "xml")
            if self.report_data.find('robot') is None:
                raise ValueError(f"<robot> tag not found in the XML file at path: {self.xml_file_path}")

        else:
            raise FileNotFoundError(f"Robot report xml file is not found at path: {self.xml_file_path}")

    def __get_test_execution_summary(self):
        """
        Used to create the test execution summary
        :return: Summary of the test case

            Format of the test summary is: ROBOFIT_TEST_EXECUTION_<date_time>_BUILD#<buildnumber>

        :rtype: String
        """
        build_info_file = self.common_keyword.get_build_info_txt_file_path()

        # Removed below because of https://visteon.atlassian.net/browse/CDCINTTION-216 request.
        """
        if build_info_file is None:
            robot_print_warning(
                f"BuildInfo.txt is not present at {build_info_file}, we are adding build info as UNKNOWN")
            return f"Robofit_TE_{self.test_type.capitalize()}_env:{self.project_manager.get_xray_environment()}"
        file = open(build_info_file, "r")
        build_value = file.readline().strip()
        build_value = build_value if build_value else "UNKNOWN"
        """

        return f"Robofit_TE_{self.test_type.capitalize()}_env:{self.project_manager.get_xray_environment()}"

    def create_info_object(self):
        """
        Used to create the test info object
        :return: Test Execution info object in dict format
        :rtype: Dict
        """
        try:
            start_time, end_time = self.__get_start_end_time(self.report_data.find_all("status")[-1])

            info = {'project': self.project_key,
                    'summary': self.__get_test_execution_summary(),
                    'description': "This execution record uploaded by ROBOFIT Framework automatically",
                    'user': str(self.project_manager.jira_user_email_id()).replace('"', ''),
                    'startDate': start_time,
                    'finishDate': end_time,
                    'testPlanKey': self.test_plan_key
                    }
            # self.logger.debug(f"Info object = {info}")
            return info
        except Exception as exp:
            robot_print_error(f"Error to create and info object, EXCEPTION: {exp}")

    def create_test_info_object(self, summary: str, test_type: str, requirement_keys: List,
                                labels: List, steps: List = None):
        """
        Used to create the test case info object.
        :param summary: Summary of the test case
        :type summary: str
        :param test_type: type of the test case. It can be Manual, Generic etc.
        :type test_type: str
        :param requirement_keys: List of requirements
        :type requirement_keys: list
        :param labels: list of labels of the test case
        :type labels: List
        :param steps: List of test steps
        :type steps: List
        :return: Dict object of test info
        :rtype: Dict
        """
        try:
            test_info = {
                "projectKey": self.project_key,
                'summary': summary,
                'type': test_type,
                'requirementKeys': requirement_keys,
                'labels': labels,
                # 'steps': steps
            }
            # self.logger.debug(f"Test info object = {test_info}")
            return test_info
        except Exception as exp:
            robot_print_error(f"Error to create an Test info object, EXCEPTION: {exp}")

    def __convert_test_status(self, status):
        """
        Covert the robot test status to the JIRA test status
        :param status: robot test case status
        :type status: str
        :return: Jira Test case Status
        :rtype: str
        """
        if status == "PASS":
            return "PASSED"
        elif status == "FAIL":
            return "FAILED"
        else:
            return "TO DO"

    def create_test_object(self, start_time, finish_time, status, test_case_info=None, test_key=None, comment=None):
        """
        Use to create test case object
        :param test:
        :type test:
        :param start_time: Start time of the test case
        :type start_time: str in format 2023-07-17T17:13:40+05:30
        :param finish_time: End time of the test case
        :type finish_time: str in format 2023-07-17T17:16:60+05:30
        :param status: Status of the test case
        :type status: str
        :param test_case_info: test case info object
        :type test_case_info: Dict
        :param comment: Comment of the test case
        :type comment: str
        :return: Dictionary of test case object
        :rtype: Dict
        """
        try:
            test_obj = {
                'start': start_time,
                'finish': finish_time,
                'executedBy': str(self.project_manager.jira_user_id()).replace('"', ''),
                'status': self.__convert_test_status(status),
            }
            if test_case_info is not None:
                test_obj["testInfo"] = test_case_info
            elif test_key is not None:
                test_obj['testKey'] = test_key
            # self.logger.debug(f"Test object = {test_obj}")
            return test_obj
        except Exception as exp:
            robot_print_error(f"Error to create test object, EXCEPTION: {exp}")

    def __get_requirement_from_test_case(self, test) -> List:
        """
        Use to get the requirement of the test case from xml
        :param test: test case xml object from lxml
        :type test: lxml.Element Object
        :return: List of all the requirement ID's
        :rtype: List
        """
        for doc in test.find_all('doc'):
            if "Requirement" in doc.get_text():
                return doc.get_text().strip().split("_")[1:]
            else:
                return []

    def __convert_time_stamps_to_local_utc(self, str_times_stamp: str) -> str:
        """
        Use to covert the time into required timestamp "2023-07-17T17:13:40+05:30"
        :param str_times_stamp: robot xml time stamp
        :type str_times_stamp: str
        :return: str format of the date time stamp like: 2023-07-17T17:13:40+05:30
        :rtype: str
        """
        return datetime.strptime(str_times_stamp, "%Y%m%d %H:%M:%S.%f").strftime(
            "%Y-%m-%dT%X+05:30")

    def __get_test_steps(self, test) -> List[Dict]:
        """
        Used to get the test steps
        :param test: xml test tag
        :type test: tag
        :return: :List of the test step dictionary
        :rtype:
        """
        return [{"action": kw.get('name'), "data": "", "result": "keyword should be pass"} for kw in
                test.find_all("kw")]

    # def __get_start_end_time_execution(self):
    #     """
    #     Used to get the start time and end time of the test case
    #     :return: str format of the start and end time
    #     :rtype: str
    #     """
    #     last_status = self.report_data.find_all("status")[-1]
    #     start_time, end_time = last_status.get("starttime"), last_status.get("endtime")
    #     if start_time is None:
    #         start_time = last_status.get("start")
    #         robot_print_error(f"Time = > {start_time}")
    #         start_time = datetime.strptime(start_time, "%Y%m%d %H:%M:%S.%f").strftime("%Y%m%d %H:%M:%S.%f")
    #     if end_time is None:
    #         end_time = datetime.now().strptime(start_time, "%Y%m%d %H:%M:%S.%f") + timedelta(
    #             seconds=float(last_status.get("elapsed")))
    #         end_time = datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y%m%d %H:%M:%S.%f")
    #     return self.__convert_time_stamps_to_local_utc(start_time), \
    #         self.__convert_time_stamps_to_local_utc(end_time)

    def __get_jira_key_from_test_case(self, test_case) -> List[str]:
        """
        This function is used to get jira keys from the user Test case Title
        :param test_case: Test case Title
        :type test_case: String
        :return: List of Test case JIRA Keys
        :rtype: List[str]
        """
        jira_keys = []
        try:
            for tag in test_case.find_all("tag"):
                if "TEST_" in tag.text:
                    key = tag.text.split("_")[-1].strip(',')  # Remove unwanted characters
                    if self.__is_valid_jira_key(key):
                        jira_keys.append(key)

            test_case_name = test_case.get("name", "")
            if test_case_name:
                possible_keys = re.findall(r"\b[A-Z][A-Z\d]+-\d+\b", test_case_name)
                for key in possible_keys:
                    if self.__is_valid_jira_key(key):
                        jira_keys.append(key)

            if not jira_keys:
                self.logger.error(f"No valid JIRA keys found in the test case: \"{test_case}\"")
        except Exception as exp:
            robot_print_error(f"Error getting JIRA keys from the test: \"{test_case}\", EXCEPTION: {exp}")

        return jira_keys

    def __is_valid_jira_key(self, key: str) -> bool:
        """
        Validate if the given string is a valid JIRA key.
        :param key: JIRA key to validate
        :type key: str
        :return: True if valid, otherwise False
        :rtype: bool
        """
        issue = self.jira_api_handler.get_issue_by_id_key(key)
        if issue:
            return True
        else:
            robot_print_error(f"The key: \"{key}\" is not a valid JIRA TEST CASE ID")
            return False

    def __is_test_name_contains_key(self, name):
        """
        Checks if the test case name contains a JIRA key matching the format "{test_proj_name}-\d+".
        :param name: Test case name
        :type name: String
        :return: True if key is found, False otherwise
        :rtype: Bool
        """
        test_proj_name = self.project_manager.get_project_test_case_key()
        return bool(re.search(fr"{test_proj_name}-\d+", name))

    def __get_start_end_time(self, status_xml_tag) -> Tuple[str, str]:
        start_time, end_time = status_xml_tag.get("starttime"), status_xml_tag.get("endtime")
        if start_time is None:
            start_time = status_xml_tag.get("start")
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y%m%d %H:%M:%S.%f")
        if end_time is None:
            end_time = datetime.now().strptime(start_time, "%Y%m%d %H:%M:%S.%f") + timedelta(
                seconds=float(status_xml_tag.get("elapsed")))
            end_time = datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y%m%d %H:%M:%S.%f")
        return self.__convert_time_stamps_to_local_utc(start_time), self.__convert_time_stamps_to_local_utc(end_time)

    def convert_xml_to_json_new(self) -> Tuple[str, List[str], str]:
        """
        Used to convert the xml report to X-Ray JSON format
        :return: JSON and Test case Key list
        :rtype: Tuple[json, List]
        """
        try:
            if self.report_data is None:
                self.__read_xml_file()
            xml_test_cases = self.report_data.find_all("test")
            for test_case in xml_test_cases:
                test_jira_keys = self.__get_jira_key_from_test_case(test_case)
                test_case_status = test_case.find_all('status')[-1]
                times = self.__get_start_end_time(test_case_status)
                for test_jira_key in test_jira_keys:
                    self.test_objs.append(
                        self.create_test_object(
                            start_time=times[0],
                            finish_time=times[1],
                            status=test_case_status.get('status'),
                            test_key=test_jira_key
                        )
                    )
                    self.test_id_list.append(test_jira_key)
                else:
                    # test case jira id is not provided by the user, so not including this test case in JSON
                    pass
            if self.existing_test_exce:
                robot_print_info(
                    f"User has provided the test execution key = {self.existing_test_exce}, "
                    f"So we are uploading the record in existing Test Execution")
                self.fina_record['testExecutionKey'] = self.existing_test_exce
            else:
                # Test Execution record needs to be created
                # As Test case Type, Group are mandatory fields.
                # We have to create the Test Execution first using Jira APIs
                result = self.jira_api_handler.create_issue_on_jira(
                    project_key=self.project_manager.get_project_test_execution_key(),
                    test_group=self.test_group,
                    test_sub_group=self.test_sub_group,
                    test_case_type=self.test_type,
                    issue_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION,
                    summary=self.__get_test_execution_summary()
                )
                if type(result) == bool and not result:
                    raise ValueError("Can not upload the record, please check the logs for more details")
                else:
                    self.fina_record['testExecutionKey'] = result
            self.fina_record['info'] = self.create_info_object()
            self.fina_record['tests'] = self.test_objs
            json_obj = json.dumps(self.fina_record, indent=4)
            with open(self.json_file_path, "w") as fp:
                fp.writelines(json_obj)
                fp.close()

            return json_obj, self.test_id_list, self.json_file_path
        except Exception as exp:
            robot_print_error(f"Error to convert the XML to JSON, EXCEPTION: {exp}")
            return '', [], ''

    @DeprecationWarning
    def convert_xml_to_json(self) -> Tuple[Union[str, None], Union[List, None]]:
        """
        This is main function which used to use to convert robot xml to JSON
        :return: Json object in str format, and list of the test case summary
        :rtype: Tuple[Union[str, None], Union[List, None]]
        """
        try:
            if self.report_data is None:
                self.__read_xml_file()
            xml_test_cases = self.report_data.find_all("test")

            for test_case in xml_test_cases:
                summary = test_case.get('name')
                status = test_case.find_all('status')[-1]
                times = self.__get_start_end_time(status)
                jira_test_cases_data = self.jira_api_handler.get_issue_by_summary(summary)
                if len(jira_test_cases_data['issues']) != 0:
                    for test_case_data in jira_test_cases_data['issues']:
                        if test_case_data['fields']['summary'] == summary:
                            self.logger.debug(f"Test case found with summary: {summary}")
                            self.test_objs.append(
                                self.create_test_object(
                                    start_time=times[0],
                                    finish_time=times[1],
                                    status=status.get('status'),
                                    test_key=test_case_data['key']))
                        else:
                            test_case_info_object = self.create_test_info_object(
                                summary=summary,
                                test_type="Manual",
                                requirement_keys=self.__get_requirement_from_test_case(test_case),
                                labels=[tag.get_text().strip() for tag in test_case.find_all('tag')],
                                # steps=self.__get_test_steps(test_case)
                            )
                            self.test_objs.append(
                                self.create_test_object(
                                    start_time=times[0],
                                    finish_time=times[1],
                                    status=status.get('status'),
                                    test_case_info=test_case_info_object))
                else:
                    # self.logger.debug(f"No test case found with summary: {summary}")
                    test_case_info_object = self.create_test_info_object(
                        summary=summary,
                        test_type="Manual",
                        requirement_keys=self.__get_requirement_from_test_case(test_case),
                        labels=[tag.get_text().strip() for tag in test_case.find_all('tag')],
                        # steps=self.__get_test_steps(test_case)
                    )
                    self.test_objs.append(
                        self.create_test_object(
                            start_time=times[0],
                            finish_time=times[1],
                            status=status.get('status'),
                            test_case_info=test_case_info_object))

                self.test_summary_list.append(summary)
            if self.existing_test_exce:
                robot_print_info(
                    f"User has provided the test execution key = {self.existing_test_exce}, "
                    f"So we are uploading the record in existing Test Execution")
                self.fina_record['testExecutionKey'] = self.existing_test_exce
            self.fina_record['info'] = self.create_info_object()
            self.fina_record['tests'] = self.test_objs

            self.logger.debug(f"final json value = {self.fina_record}")

            json_obj = json.dumps(self.fina_record, indent=4)
            with open(self.json_file_path, "w") as fp:
                fp.writelines(json_obj)
                fp.close()
            # if self.__validate_xray_json(json_obj):
            #     robot_print_debug(f"json file path {self.json_file_path}")
            return json_obj, self.test_summary_list
            # return None, None
        except Exception as exp:
            robot_print_error(f'Error to parse the xml file, EXCEPTION: {exp}')
            return None, None

    def __validate_xray_json(self, json_record) -> bool:
        """
        Use to validate the xray JSON
        :param json_record: Converted JSON object
        :type json_record: json object
        :return: True if validate otherwise false
        :rtype: bool
        """
        try:
            validate(json_record, schema=json.load(open(os.path.join(self.common_keyword.get_root_path(), ROBO_FIT,
                                                                     ROBO_LIBS, ROBO_COMPONENTS, XRAY_UTILITY_MODULE,
                                                                     "schema.json"), "r")))
            return True
        except SchemaError as exp:
            robot_print_error(f"Invalid schema provided, please check schema : "
                              f"{os.path.join(self.common_keyword.get_root_path(), ROBO_FIT, ROBO_LIBS, ROBO_COMPONENTS, XRAY_UTILITY_MODULE, 'schema.json')},"
                              f" EXCEPTION: {exp}")
            return False

    def create_test_step_object(self, xml_test):
        """
        Use to create the test step object
        :param xml_test: test case tag from robot xml file
        :type xml_test: tag value
        :return: List of test steps
        :rtype: List of Dictionary
        """
        return [{"action": kw.get('name')} for kw in xml_test.find_all('kw')]

    def convert_xml_to_json_with_df(self) -> Tuple[str, List[str], str]:
        """
        Used to convert the xml report to X-Ray JSON format
        :return: JSON and Test case Key list
        :rtype: Tuple[json, List]
        """
        try:
            if self.report_data is None:
                self.__read_xml_file()
            xml_test_cases = self.report_data.find_all("test")
            for test_case in xml_test_cases:
                test_jira_keys = self.__get_jira_key_from_test_case(test_case)
                test_case_status = test_case.find_all('status')[-1]
                times = self.__get_start_end_time(test_case_status)
                if test_jira_keys:
                    for test_jira_key in test_jira_keys:
                        self.test_objs.append(
                            self.create_test_object(
                                start_time=times[0],
                                finish_time=times[1],
                                status=test_case_status.get('status'),
                                test_key=test_jira_key
                            )
                        )
                        self.test_id_list.append(test_jira_key)
                else:
                    self.df = self.converter.create_test_case_dataframe()
                    issue_summary = test_case.get('name')
                    if issue_summary and self.df is not None:
                        matching_rows = self.df[self.df['summary'] == issue_summary]
                        if not matching_rows.empty:
                            issue_row = matching_rows.iloc[0]
                            test_key = issue_row['key']
                            if test_key:
                                if test_key.startswith("TEST_"):
                                    test_key = test_key.replace("TEST_", "")
                                self.test_objs.append(
                                    self.create_test_object(
                                        start_time=times[0],
                                        finish_time=times[1],
                                        status=test_case_status.get('status'),
                                        test_key=test_key
                                    )
                                )
                                self.test_id_list.append(test_key)
                            else:
                                robot_print_error(
                                    f"Test case with summary '{issue_summary}' does not have a corresponding key in DataFrame.")
                        else:
                            robot_print_error(
                                f"No matching rows found in DataFrame for test case summary '{issue_summary}'.")
                    else:
                        robot_print_error("Test case summary or DataFrame does not match any of the test case.")
            if self.existing_test_exce:
                robot_print_info(
                    f"User has provided the test execution key = {self.existing_test_exce}, "
                    f"So we are uploading the record in existing Test Execution")
                self.fina_record['testExecutionKey'] = self.existing_test_exce
            else:
                # Test Execution record needs to be created
                # As Test case Type, Group are mandatory fields.
                # We have to create the Test Execution first using Jira APIs
                result = self.jira_api_handler.create_issue_on_jira(
                    project_key=self.project_manager.get_project_test_execution_key(),
                    test_group=self.test_group,
                    test_sub_group=self.test_sub_group,
                    test_case_type=self.test_type,
                    issue_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION,
                    summary=self.__get_test_execution_summary()
                )
                if type(result) == bool and not result:
                    raise ValueError("Can not upload the record, please check the logs for more details")
                else:
                    self.fina_record['testExecutionKey'] = result
            self.fina_record['info'] = self.create_info_object()
            self.fina_record['tests'] = self.test_objs
            json_obj = json.dumps(self.fina_record, indent=4)
            with open(self.json_file_path, "w") as fp:
                fp.writelines(json_obj)
                fp.close()

            return json_obj, self.test_id_list, self.json_file_path
        except Exception as exp:
            robot_print_error(f"Error to convert the XML to JSON, EXCEPTION: {exp}")
            return '', [], ''
