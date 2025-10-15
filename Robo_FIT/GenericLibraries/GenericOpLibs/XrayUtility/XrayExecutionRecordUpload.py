import json
import logging
import os.path
import subprocess
from typing import List, Dict, Any, Union

import pandas as pd
import requests
from requests import Response
from requests.exceptions import SSLError

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ROBOT_REPORT_FOLDER_NAME, \
    ROBOT_REPORT_XML_FILE_NAME, ROBOT_REPORT_HTML_FILE_NAME, ROBOT_LOG_HTML_FILE_NAME, PERFORMANCE_UTILISATION_DIR
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

    # request methods
    __req_method_get = "GET"
    __req_method_post = "POST"
    __req_method_put = "PUT"
    __req_method_delete = "DELETE"

    def __init__(self):
        self.project_config_manager = ProjectConfigManager()
        self.common_keyword_manager = CommonKeywordsClass()
        self.xray_auth = None
        self.auth = None
        self.jira_api_handler = JiraApiHandler()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.df = None

    def __get_user_auth(self, client_auth) -> str:
        """
        This function will authenticate the user
        :param client_auth: Client info like client_id and client_secret
        :type client_auth: String
        :return: Authentication token
        :rtype: String
        """
        try:
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
            if response.status_code == 200:
                robot_print_info(f"AUTH Token: {self.xray_auth}")
                return self.xray_auth
            elif response.status_code == 401:
                error_message = "Authentication failed due to invalid client credentials. Please check your client ID " \
                                "and secret. "
                robot_print_error(f"{error_message} This is not a framework issue.")
                self.logger.error(f"Response content: {response.text}")
                raise ValueError(error_message)
            else:
                error_message = f"Authentication failed with status code {response.status_code}: {response.text}"
                robot_print_error(error_message)
                self.logger.error(error_message)
                raise ValueError(error_message)
        except requests.exceptions.SSLError as ssl_error:
            robot_print_error(f"SSL Error during authentication: {ssl_error} Please check your zscaler certificate path.")
            self.logger.error(f"SSL Error: {ssl_error}")
            raise ssl_error
        except Exception as exp:
            robot_print_error(f"Error during authentication: {exp}")
            self.logger.error(f"Exception: {exp}")
            raise exp

    def __send_xray_request(self, url: str, method: str, headers: Dict, payload: Union[Dict, str, None] = None,
                            params: Union[Dict, None] = None, json_data: Union[Dict, None] = None, is_auth_request: bool = False) -> Response:
        try:
            if not is_auth_request:
                auth = self.__get_user_auth(client_auth=self.project_config_manager.xray_client_info())
                if headers.get("Authorization") is None:
                    headers['Authorization'] = f'Bearer {auth}'

            if method == XrayExecutionRecordUpload.__req_method_post or method == XrayExecutionRecordUpload.__req_method_put:
                return requests.request(method,
                                        url,
                                        headers=headers,
                                        data=payload,
                                        json=json_data,
                                        verify=self.project_config_manager.get_certificate_path())
            elif method == XrayExecutionRecordUpload.__req_method_get:
                return requests.request(method,
                                        url,
                                        headers=headers,
                                        params=params,
                                        verify=self.project_config_manager.get_certificate_path())
            else:
                raise ValueError(f"Given REST method '{method}' is not supported")
        except SSLError as exp:
            robot_print_error(f"CERTIFICATE_VERIFY_FAILED, EXCEPTION: {exp}")

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
            data = self.__get_robot_xml_data()
            headers = {
                "Content-Type": "text/xml",
            }
            url = XrayExecutionRecordUpload.__UPLOAD_URL.format(
                projectkey=self.project_config_manager.get_project_test_execution_key())
            response = self.__send_xray_request(url=url, method=XrayExecutionRecordUpload.__req_method_post,
                                                headers=headers, payload=data)
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
            headers = {
                "Content-Type": "application/json",
            }
            response = self.__send_xray_request(url=XrayExecutionRecordUpload.__UPLOAD_JSON_URL,
                                                method=XrayExecutionRecordUpload.__req_method_post,
                                                headers=headers, payload=json_test_exec_record)
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

    def new_upload_xray_test_execution_record_by_json(self, json_file_path: str) -> Any | None:
        """
        Used to upload the xray test case record by JSON format.
        :type json_file_path: str
        :return: True if successfully updated otherwise False
        :rtype: Bool
        """
        global test_execution_id
        test_execution_id = None
        try:
            client_info = self.project_config_manager.xray_client_info()
            auth = self.__get_user_auth(client_auth=client_info)
            curl_command = [
                'curl',
                '-v',  # Verbose flag
                '-X', 'POST',
                XrayExecutionRecordUpload.__UPLOAD_JSON_URL,
                '-H', 'Content-Type: application/json',
                '-H', f'Authorization: Bearer {auth}',
                '--data', f'@{json_file_path}'
            ]
            result = subprocess.run(curl_command, capture_output=True, text=True)
            robot_print_info(f"Upload execution record response: {result.stdout}")
            if result.returncode == 0:
                try:
                    response_json = json.loads(result.stdout)

                    # Check if the response contains expected fields
                    if "id" in response_json and "key" in response_json:
                        robot_print_info("Record uploaded successfully.")
                        robot_print_info(f"Issue Key: {response_json['key']}")
                        test_execution_id = response_json["id"]
                        # test_execution_id = response_json["key"]
                        return response_json
                    else:
                        robot_print_info("Response does not contain expected fields.")
                        return None
                except json.JSONDecodeError:
                    self.logger.error("Response is not valid JSON.")
                    self.logger.error(f"Response Content: {result.stdout}")
                    return None
            else:
                robot_print_error(f"cURL command failed with return code: {result.returncode}")
                robot_print_error(f"Error Output: {result.stderr}")
                return None
        except Exception as exp:
            robot_print_error(f"Error uploading the Xray JSON test execution record: {json_file_path}, "
                              f"EXCEPTION: {exp}")
            return None

    def __get_test_cases_link_to_test_execution(self, execution_id: str) -> List:
        """
        Used to get the test cases linked to the given execution id
        :param execution_id: String value of execution id
        :type execution_id: String
        :return: List of test cases id linked to given test execution id
        :rtype: List
        """
        try:
            headers = {
                "Content-Type": "application/json",
            }
            results = []
            is_all_result_fetched = False
            start_point = 0
            while not is_all_result_fetched:
                body = """{getTestExecutions(issueIds: """
                body += f"\"{execution_id}\"" + ", limit: 10) {\nresults {\n"
                body += f"tests(limit: 100, start:{start_point})"
                body += "{\nresults{\nissueId\njira(fields: [\"key\"])}}}}}"
                response = self.__send_xray_request(url=XrayExecutionRecordUpload.__XRAY_GRAPHQL_URL,
                                                    method=XrayExecutionRecordUpload.__req_method_post,
                                                    headers=headers, json_data={"query": body})
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
            robot_print_error(f"Error to get the test execution record, EXCEPTION: {exp}")

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
            json_test_exec_record, test_id_list, json_file_path = ConvertXmlToJson(
                existing_test_exec=test_execution_key, test_plan_key=test_plan_key,
                test_sub_group=test_sub_group, test_group=test_group, test_type=test_type,
                test_report_path=test_report_path).convert_xml_to_json_new()
            if json_test_exec_record is None or test_id_list is None:
                raise ValueError("Given values is not in proper format, Can't upload JSON record")
            robot_print_info(f"After conversions data is = {json_test_exec_record}")
            # response = self.upload_xray_test_execution_record_by_json(json_test_exec_record=json_test_exec_record)
            # Due to issue CDCINTTION-2750 we are now using curl command to upload the record not API
            response = self.new_upload_xray_test_execution_record_by_json(json_file_path=json_file_path)
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

    def start_upload_test_cases_record(self, test_execution_key, test_plan_key, test_sub_group, test_group,
                                       test_type, build_version, test_report_path=None):
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
            json_test_exec_record, test_id_list, json_file_path = ConvertXmlToJson(
                existing_test_exec=test_execution_key, test_plan_key=test_plan_key,
                test_sub_group=test_sub_group, test_group=test_group, test_type=test_type,
                test_report_path=test_report_path).convert_xml_to_json_with_df()
            if json_test_exec_record is None or test_id_list is None:
                raise ValueError("Given values is not in proper format, Can't upload JSON record")
            robot_print_info(f"After conversions data is = {json_test_exec_record}")
            # Due to issue CDCINTTION-2750 we are now using curl command to upload the record not API
            response = self.new_upload_xray_test_execution_record_by_json(json_file_path=json_file_path)
            # response = self.upload_xray_test_execution_record_by_json(json_test_exec_record=json_test_exec_record)
            if response is not None:
                self.logger.debug(f"issuedIds: {test_id_list}")
                tc_status = self.jira_api_handler.update_custom_field_of_all_test_cases(issue_ids=test_id_list,
                                                                                        test_group=test_group,
                                                                                        test_sub_group=test_sub_group,
                                                                                        test_type=test_type,
                                                                                        issue_type=JiraApiHandler.ISSUE_TYPE_TEST,
                                                                                        build_version=build_version,
                                                                                        project_key=self.project_config_manager.get_project_test_case_key())
                self.df = pd.DataFrame(tc_status)
                excel_path = self.jira_api_handler.get_state_transition_excel_file()
                self.df.to_excel(excel_path, index=False)
                self.jira_api_handler.update_custom_field_of_all_test_cases(issue_ids=[response['id']],
                                                                            test_group=test_group,
                                                                            test_sub_group=test_sub_group,
                                                                            test_type=test_type,
                                                                            issue_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION,
                                                                            build_version=build_version,
                                                                            project_key=self.project_config_manager.get_project_test_execution_key())
        except IOError as exp:
            robot_print_error(f"Error to read the robot json report, EXCEPTION {exp}")
            return False
        except Exception as exp:
            robot_print_error(f"Error to upload X-Ray execution record, EXCEPTION: {exp}")
            return False

    def __process_performance_utilization(self, performance_utilization_path: str):
        """
        Processes performance utilization files within the specified path.
        Checks for the 'PerformanceUtilisation' folder in the provided path and searches for '.html', '.log', and '.xlsx' files.
        :param performance_utilization_path: Path to check for the 'PerformanceUtilisation' folder.
        Returns:a list of found files or an empty list if none are found or the folder doesn't exist.
        """
        if performance_utilization_path is None:
            robot_print_info("Performance utilization path is None.")
            return []

        if not os.path.exists(performance_utilization_path) or not os.path.isdir(performance_utilization_path):
            self.logger.info(f"PerformanceUtilisation folder does not exist at: {performance_utilization_path}")
            return []

        required_files = ['.html', '.log', '.xlsx']
        additional_files = self.__get_additional_files(performance_utilization_path, required_files)

        if additional_files:
            file_paths = []
            for file_tuple in additional_files:
                file_path = file_tuple[1][1].name
                file_paths.append(file_path)
                self.logger.info(f"File Path: {file_path}")
            return file_paths
        else:
            robot_print_info("No files found in PerformanceUtilisation folder.")
            return []

    def __get_additional_files(self, performance_utilisation_folder, required_files):
        """
        Check for the existence of additional files in all subdirectories based on the list of required file types.
        :param performance_utilisation_folder: The directory path to check for the files (PerformanceUtilisation folder).
        :param required_files: A list of file types/extensions to check for.
        :return: A set of file tuples to be processed.
        """
        files = set()

        for root, dirs, filenames in os.walk(performance_utilisation_folder):
            for filename in filenames:
                for file_type in required_files:
                    if filename.lower().endswith(file_type.lower()):
                        file_path = os.path.join(root, filename)
                        try:
                            with open(file_path, 'rb') as file:
                                files.add(('file', (filename, file)))
                        except Exception as e:
                            robot_print_error(f"Error opening file {file_path}: {e}")

        return files

    def jira_report_upload(self, test_report_path=None):
        files_to_upload = []
        try:
            if test_execution_id is not None:
                url = self.project_config_manager.jira_server_domain_url().replace('"', "")
                url = f"{url}/rest/api/3/issue/{test_execution_id}/attachments"

                if test_report_path:
                    html_report_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME,
                                                         ROBOT_REPORT_HTML_FILE_NAME)
                    html_log_file_path = os.path.join(test_report_path, ROBOT_REPORT_FOLDER_NAME,
                                                      ROBOT_LOG_HTML_FILE_NAME)
                    performance_utilization_path = os.path.join(test_report_path, PERFORMANCE_UTILISATION_DIR)
                else:
                    html_report_file_path = self.common_keyword_manager.get_robot_html_report_path()
                    html_log_file_path = self.common_keyword_manager.get_robot_html_log_path()
                    performance_utilization_path = self.common_keyword_manager.get_performance_utilization_path()

                additional_file_paths = self.__process_performance_utilization(performance_utilization_path)
                if html_report_file_path and html_log_file_path is not None:
                    files_to_upload.append(('file', ('test_report.html', open(html_report_file_path, 'rb'))))
                    files_to_upload.append(('file', ('test_log.html', open(html_log_file_path, 'rb'))))

                for file_path in additional_file_paths:
                    if os.path.exists(file_path):
                        files_to_upload.append(('file', (os.path.basename(file_path), open(file_path, 'rb'))))

                if files_to_upload:
                    self.logger.info(f"Files to upload: {files_to_upload}")
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
                        files=files_to_upload,
                        auth=self.auth,
                        verify=False
                    )
                    robot_print_info(f"Upload Test Reports response: {response.status_code}")
                    if response.status_code == 200:
                        robot_print_info(f"{'=' * 20} Test Reports Upload Status {'=' * 20}")
                        self.logger.info(
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
                            f"413 Request Entity Too Large: The attachments exceed the maximum attachment size for "
                            f"issues/more than 60 files are requested to be uploaded")
                        return {}
                    else:
                        robot_print_error(f"Unknown response with status code: {response.status_code}")
                        return {}
                else:
                    robot_print_info("No files to upload.")
            else:
                robot_print_error(f"Test execution id was not found: {test_execution_id}")
        except Exception as exp:
            robot_print_error(f"Error to upload the test execution report and log.html to test execution record: {exp}")
            return {}
        finally:
            for _, (_, file) in files_to_upload:
                file.close()
