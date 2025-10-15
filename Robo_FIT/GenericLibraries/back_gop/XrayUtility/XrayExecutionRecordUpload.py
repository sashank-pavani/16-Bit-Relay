import json
import logging
import os.path
from typing import List, Dict

import certifi
import requests
from requests.auth import HTTPBasicAuth

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ROBOT_REPORT_FOLDER_NAME, \
    ROBOT_REPORT_XML_FILE_NAME, ROBOT_REPORT_HTML_FILE_NAME, ROBOT_LOG_HTML_FILE_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info, \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.ConvertXmlToJson import ConvertXmlToJson
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.JiraApiHandler import JiraApiHandler


class XrayExecutionRecordUpload:
    __AUTH_UTL = "https://xray.cloud.getxray.app/api/v1/authenticate"
    __VISTEON_ZSCALER_CER_URL = "https://visteon.service-now.com/sys_attachment.do?sys_id=61aa31eddbf46f44fc90dd3b5e961926"
    __UPLOAD_URL = "https://xray.cloud.getxray.app/api/v1/import/execution/robot/?projectKey={projectkey}"
    __UPLOAD_JSON_URL = "https://xray.cloud.getxray.app/api/v1/import/execution"
    __XRAY_GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"

    def __init__(self):
        self.project_config_manager = ProjectConfigManager()
        self.common_keyword_manager = CommonKeywordsClass()
        self.xray_auth = None
        self.logger = logger
        self.auth = None
        self.jira_api_handler = JiraApiHandler()
        self.logger = logging.getLogger(self.__class__.__name__)

    def __get_user_auth(self, client_auth) -> str:
        """
        This function will authenticate the user
        :param client_auth: Client info like client_id and client_secret
        :type client_auth: String
        :return: Authentication token
        :rtype: String
        """
        self.logger.debug(f"Certificate : {self.project_config_manager.get_certificate_path()}")
        auth_headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(
            XrayExecutionRecordUpload.__AUTH_UTL,
            headers=auth_headers,
            data=client_auth,
            verify=self.project_config_manager.get_certificate_path()
        )
        self.xray_auth = response.text.replace('"', '')
        robot_print_info(f"AUTH: Response status = {response.status_code}")
        robot_print_info(self.xray_auth)
        return self.xray_auth

    def __get_robot_xml_data(self) -> str:
        """
        This function read the XML report of robot framework
        :return: Content of the XML file
        :rtype: String
        """
        try:
            data = None
            robot_xml_file_path = os.path.join(self.common_keyword_manager.get_report_path(), ROBOT_REPORT_FOLDER_NAME,
                                               ROBOT_REPORT_XML_FILE_NAME)
            # self.logger.debug(f"Uploading record: {robot_xml_file_path}")
            if os.path.isfile(robot_xml_file_path):
                with open(robot_xml_file_path, "r") as fp:
                    lines = fp.readlines()
                    data = "".join(lines)
                return data
            else:
                raise FileNotFoundError(f"Report is not available at path: {robot_xml_file_path}")
        except Exception as exp:
            robot_print_error(f"Error to get the robot xml data, EXCEPTION: {exp}")

    def upload_execution_record(self) -> bool:
        """
        This function will upload the execution record.
        :return: True if upload successfully, otherwise False
        :rtype: Bool
        """
        try:
            client_info = self.project_config_manager.xray_client_info()
            data = self.__get_robot_xml_data()
            robot_print_info(f"Client info: type: {type(client_info)} and info: {client_info}")
            auth = self.__get_user_auth(client_auth=client_info)
            headers = {
                "Content-Type": "text/xml",
                "Authorization": f'Bearer {auth}'
            }
            response = requests.request(
                "POST",
                XrayExecutionRecordUpload.__UPLOAD_URL.format(
                    projectkey=self.project_config_manager.get_project_test_execution_key()),
                headers=headers,
                data=data,
                verify=self.project_config_manager.get_certificate_path()
            )
            robot_print_info(f"Upload execution record response: {response.status_code}")
            if response.status_code == 200:
                robot_print_info(f"{'=' * 20} Xray Upload Status {'=' * 20}")
                robot_print_info(f"{response.json()}")
                robot_print_info(f"{'=' * 40}")
                return True
            return False
        except IOError as exp:
            robot_print_error(f"Error to read the robot xml report, EXCEPTION {exp}")
            return False
        except Exception as exp:
            robot_print_error(f"Error to upload X-Ray execution record, EXCEPTION: {exp}")
            return False

    def __get_test_record_by_jql_query(self, search_query: str, fields: List = ["id", "key", "summary"]) -> Dict:
        """
        This function is used to get the test record from JIRA.
        THis function will return the test record
        :param fields: list of filed which test case container, default values = ["id", "key", "summary"]
        :type fields: List[str]
        :param search_query: JQL Query to get the record from JIRA
        :type search_query: string
        :return: If record found it will return Dict format of data otherwise empty dict.
        :rtype: Dict
        """
        response = None
        try:
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/search"
            auth = HTTPBasicAuth(self.project_config_manager.jira_user_email_id(),
                                 self.project_config_manager.jira_api_token())
            headers = {
                "Accept": "application/json"
            }
            query = {
                'jql': search_query,
                'maxResults': 10000,
                'validateQuery': 'strict',
                'fields': 'id, key, summary'
            }
            response = requests.request(
                "GET",
                url,
                headers=headers,
                params=query,
                auth=auth,
                verify=self.project_config_manager.get_certificate_path()
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                robot_print_error(f"400 BAD REQUEST: Invalid jql query => {query}")
                return {}
            elif response.status_code == 401:
                robot_print_error(f"401 UNAUTHORIZED: authentication credentials are incorrect or missing. "
                                  f"Please check configuration file")
                return {}
            else:
                robot_print_error(f"Unknown response with status code: {response.status_code}")
                return {}
        except json.JSONDecodeError as json_error:
            robot_print_error(f"Error to decode the response {response.text if response is not None else ''}, "
                              f"EXCEPTION: {json_error}")
        except Exception as exp:
            robot_print_error(f"Error to upload custom filed, EXCEPTION: {exp}")

    def upload_xray_test_execution_record_by_json(self, json_test_exec_record) -> Dict:
        """
        Used to upload the xray test case record by JSON format.
        :param json_test_exec_record: json format value in string
        :type json_test_exec_record: String
        :return: True if successfully updated otherwise False
        :rtype: Bool
        """
        global test_execution_id
        test_execution_id = None
        try:
            client_info = self.project_config_manager.xray_client_info()
            auth = self.__get_user_auth(client_auth=client_info)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f'Bearer {auth}'
            }
            response = requests.request(
                "POST",
                XrayExecutionRecordUpload.__UPLOAD_JSON_URL,
                headers=headers,
                data=json_test_exec_record,
                verify=self.project_config_manager.get_certificate_path()
            )
            robot_print_info(f"Upload execution record response: {response.status_code}")
            if response.status_code == 200:
                robot_print_info(f"{'=' * 20} Xray Upload Status {'=' * 20}")
                robot_print_info(f"{response.json()}, {response.content}")
                test_execution_id = response.json()
                test_execution_id = test_execution_id['key']
                robot_print_info(f"{'=' * 40}")
                return response.json()
            elif response.status_code == 400:
                robot_print_error(f"400 BAD REQUEST: No execution results were provided, RESPONSE: {response.text}")
            elif response.status_code == 401:
                robot_print_error(f"401 UNAUTHORIZED: The Xray license/credentials is not valid, "
                                  f"RESPONSE: {response.text}")
            elif response.status_code == 500:
                robot_print_error(f"500  INTERNAL SERVER ERROR: An internal error occurred when importing execution "
                                  f"results, RESPONSE: {response.text}")
        except Exception as exp:
            robot_print_error(f"Error to upload the xray json test execution record: {json_test_exec_record}, "
                              f"EXCEPTION: {exp}")

    def __get_test_cases_link_to_test_execution(self, execution_id: str) -> List:
        """
        Used to get the test cases linked to the given execution id
        :param execution_id: String value of execution id
        :type execution_id: String
        :return: List of test cases id linked to given test execution id
        :rtype: List
        """
        try:
            if self.xray_auth is None:
                client_info = self.project_config_manager.xray_client_info()
                self.xray_auth = self.__get_user_auth(client_auth=client_info)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f'Bearer {self.xray_auth}'
            }
            results = []
            is_all_result_fetched = False
            start_point = 0
            while not is_all_result_fetched:
                body = """{getTestExecutions(issueIds: """
                body += f"\"{execution_id}\"" + ", limit: 10) {\nresults {\n"
                body += f"tests(limit: 100, start:{start_point})"
                body += "{\nresults{\nissueId\njira(fields: [\"key\"])}}}}}"
                response = requests.post(url=XrayExecutionRecordUpload.__XRAY_GRAPHQL_URL,
                                         json={"query": body},
                                         headers=headers,
                                         verify=self.project_config_manager.get_certificate_path())
                if response.status_code == 200:
                    response_result = response.json()['data']['getTestExecutions']['results'][0]['tests']['results']
                    results.extend(response_result)
                    if len(response_result) == 100:
                        robot_print_debug(f"Fetched 100 test cases linked to test execution: {execution_id},"
                                          f"It seems more test cases are linked so fetching them")
                        start_point += 100
                    else:
                        is_all_result_fetched = True
                else:
                    robot_print_debug(f"response status: f{response.status_code}, content: {response.content}")
            return results
        except Exception as exp:
            robot_print_error(f"Errro to get the test execution record, EXCEPTION: {exp}")

    def start_upload_xray_record_by_json(self, test_execution_key, test_plan_key, test_sub_group,
                                         test_group, test_type, build_version, test_report_path=None):
        """
        Used to start updating X-ray record by using JSON format.

        If a user doesn't provide test execution key then new record will be created
        If user provides a test execution key, then the same record will be updated.

        :param test_sub_group:
        :type test_sub_group:
        :param test_group:
        :type test_group:
        :param test_type:
        :type test_type:
        :param test_group:
        :type test_group:
        :param test_plan_key:
        :type test_plan_key:
        :param test_execution_key: test execution key in string format
        :type test_execution_key: String
        :param build_version:
        :type build_version:
        :param test_report_path: The path to the test report. Defaults to None
        :type test_report_path: String
        :return: None
        :rtype: None
        """
        try:
            json_test_exec_record, test_id_list = ConvertXmlToJson(
                existing_test_exec=test_execution_key, test_plan_key=test_plan_key,
                test_sub_group=test_sub_group, test_group=test_group, test_type=test_type,
                test_report_path=test_report_path).convert_xml_to_json_new()
            if json_test_exec_record is None or test_id_list is None:
                raise ValueError("Given values is not in proper format, Can't upload JSON record")
            robot_print_info(f"After conversions data is = {json_test_exec_record}")
            response = self.upload_xray_test_execution_record_by_json(json_test_exec_record=json_test_exec_record)
            if response is not None:
                self.logger.debug(f"issuedIds: {test_id_list}")
                # self.logger.debug(
                #     f"Updated custom filed customfield_10505 of issues : {test_id_list}, size={len(test_id_list)}")
                tc_status = self.jira_api_handler.update_custom_field_of_test_case(issue_ids=test_id_list,
                                                                                   test_group=test_group,
                                                                                   test_sub_group=test_sub_group,
                                                                                   test_type=test_type,
                                                                                   issue_type=JiraApiHandler.ISSUE_TYPE_TEST,
                                                                                   build_version=build_version,
                                                                                   project_key=self.project_config_manager.get_project_test_case_key())
                self.logger.debug(f"status of test case custom filed update is = "
                                  f"{tc_status}")
                te_status = self.jira_api_handler.update_custom_field_of_test_case(issue_ids=[response['id']],
                                                                                   test_group=test_group,
                                                                                   test_sub_group=test_sub_group,
                                                                                   test_type=test_type,
                                                                                   issue_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION,
                                                                                   build_version=build_version,
                                                                                   project_key=self.project_config_manager.get_project_test_execution_key())
                self.logger.debug(f"status of test execution custom filed update is = "
                                  f"{te_status}")
        except IOError as exp:
            robot_print_error(f"Error to read the robot json report, EXCEPTION {exp}")
            return False
        except Exception as exp:
            robot_print_error(f"Error to upload X-Ray execution record, EXCEPTION: {exp}")
            return False

    def jira_report_upload(self, test_report_path=None):
        """
        This function Adds one or more attachments to an issue.
        Attachments are posted as multipart/form-data.
        test execution id is taken from the response of upload_xray_test_execution_record_by_json function.
        :return: List of attachments added and  id linked to given test execution id
        """
        try:
            if test_execution_id is not None:
                url = self.project_config_manager.jira_server_domain_url().replace('"', "")
                url = f"{url}/rest/api/3/issue/{test_execution_id}/attachments"
                if test_report_path:
                    html_report_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME,
                                                         ROBOT_REPORT_HTML_FILE_NAME)
                    html_log_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME,
                                                      ROBOT_LOG_HTML_FILE_NAME)
                else:
                    html_report_file_path = self.common_keyword_manager.get_robot_html_report_path()
                    html_log_file_path = self.common_keyword_manager.get_robot_html_log_path()
                if html_report_file_path and html_log_file_path is not None:
                    files = {
                        ('file', ('test_report.html', open(html_report_file_path, 'rb'))),
                        ('file', ('test_log.html', open(html_log_file_path, 'rb')))
                    }
                    headers = {
                        "X-Atlassian-Token": "no-check"
                    }
                    if self.auth is None:
                        self.auth = (self.project_config_manager.jira_user_email_id().replace('"', ""),
                                     self.project_config_manager.jira_api_token().replace('"', ""))
                    response = requests.request(
                        "POST",
                        url,
                        headers=headers,
                        files=files,
                        auth=self.auth,
                        verify=False
                    )
                    robot_print_info(f"Upload Test Reports response: {response.status_code}")
                    if response.status_code == 200:
                        robot_print_info(f"{'=' * 20} Test Reports Upload Status {'=' * 20}")
                        robot_print_info(
                            json.dumps(obj=json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
                        )
                        robot_print_info(f"{'=' * 20} Test Reports Uploaded Successfully {'=' * 20}")
                        return response.json()
                    elif response.status_code == 403:
                        robot_print_error(f"403 Forbidden: User does not have the necessary permission")
                        return {}
                    elif response.status_code == 404:
                        robot_print_error(
                            f"404 Not Found: The Issue is not found/User does not have permission to view the issue")
                        return {}
                    elif response.status_code == 413:
                        robot_print_error(
                            f"413 Request Entity Too Large: The attachments exceed the maximum attachment size for issues/more than 60 files are requested to be uploaded")
                        return {}
                    else:
                        robot_print_error(f"Unknown response with status code: {response.status_code}")
                        return {}
                else:
                    raise FileNotFoundError(
                        f"No HTML files were found at the specified path: {html_report_file_path, html_log_file_path}")
            else:
                robot_print_error(f"test execution id was not found.{test_execution_id}")
        except Exception as exp:
            robot_print_error(f"Error to upload the test execution report and log.html to test execution record: {exp}")
            return {}
