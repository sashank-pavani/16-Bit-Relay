import json
import os
import time
import requests
import logging

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info, robot_print_error, \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.JiraApiHandler import JiraApiHandler, IssueTypeTestData
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.TcUpload.ConvertRobotToExcel import ConvertRobotToExcel
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.XrayApiHandler import XrayApiHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.XrayExecutionRecordUpload import XrayExecutionRecordUpload


class XrayTestCaseUpload:
    __AUTH_URL = "https://xray.cloud.getxray.app/api/v2/authenticate"
    __IMPORT_BULK_TC_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk/?projectKey={project_key}"
    __JOB_COMPLETION_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk/{job_id}/status"

    FIELD_MAPPING = {
        'Test Case Key': 'testKey',
        'Test Case Summary': 'summary',
        'Test Steps': 'gherkin_def',
        'Labels': 'labels',
        'Feature Group': 'featureGroup'
    }

    JOB_STATUS_MAP = {
        "pending": "PENDING",
        "working": "RUNNING",
        "failed": "FAILED",
        "successful": "COMPLETED",
        "partially_successful": "PARTIALLY_COMPLETED",
        "unsuccessful": "UNSUCCESSFUL"
    }

    def __init__(self):
        self.project_config_manager = ProjectConfigManager()
        self.xray_auth = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.auth = None
        self.jira_api_handler = JiraApiHandler()
        self.converter = ConvertRobotToExcel()
        self.xray_api_handler = XrayApiHandler()
        self.xray_execution_upload = XrayExecutionRecordUpload()
        self.df = None

    def import_test_bulk(self, test_group, test_sub_group, test_type):
        """
        Upload test cases in bulk to Xray.
        Args:
            test_group (str): Test group name.
            test_sub_group (str): Test sub-group name.
            test_type (str): Test case type.
        Returns list: List of dictionaries containing uploaded issues' ID and key.
        """
        client_info = self.project_config_manager.xray_client_info()
        auth = self.xray_api_handler.get_user_auth(client_auth=client_info)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth}"
        }

        try:
            json_file_path = self.converter.convert_to_json_format(test_group=test_group, test_sub_group=test_sub_group,
                                                                   test_case_type=test_type)
            with open(json_file_path, 'r') as file:
                data = json.load(file)

            response = requests.request("POST",
                                        XrayTestCaseUpload.__IMPORT_BULK_TC_URL.format(
                                            project_key=self.project_config_manager.get_project_test_case_key()),
                                        headers=headers,
                                        json=data,
                                        verify=self.project_config_manager.get_certificate_path())
            response.raise_for_status()
            self.logger.info(f"Upload test case response: {response.status_code}")

            job_id = response.json().get('jobId')
            if job_id:
                uploaded_issues = self.wait_for_job_completion(job_id)
                self.logger.info(f"Uploaded issues ID and Key:{uploaded_issues}")
                return uploaded_issues
            else:
                self.logger.info("No job ID found in the response.")
        except (IOError, json.JSONDecodeError) as exp:
            self.logger.error(f"Error reading or parsing the JSON file: {exp}")
        except requests.exceptions.RequestException as exp:
            self.logger.error(f"Error uploading test cases to Xray: {exp}")

    def extract_issue_id_key_from_result(self, xray_tc_bulk_upload_res: dict) -> list:
        """
        Extract issue ID and key from the bulk upload result.
        Args:
            xray_tc_bulk_upload_res (dict): The result dictionary from the Xray bulk upload response.
        Returns list: List of dictionaries containing issue ID and key.
        """
        uploaded_issues = []
        issues = xray_tc_bulk_upload_res.get('issues', [])
        for issue in issues:
            issue_id = issue.get('id')
            issue_key = issue.get('key')
            uploaded_issues.append({
                'issue_id': issue_id,
                'issue_key': issue_key
            })
        return uploaded_issues

    def wait_for_job_completion(self, job_id: str):
        """
        Wait for completion of a bulk test import job in Xray.
        Args:
            job_id (str): ID of the job for bulk test import.
        Returns list: List of dictionaries containing uploaded issues' ID and key.
        """
        uploaded_issues = []

        url = XrayTestCaseUpload.__JOB_COMPLETION_URL.format(job_id=job_id)
        client_info = self.project_config_manager.xray_client_info()
        auth = self.xray_api_handler.get_user_auth(client_auth=client_info)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth}"
        }
        max_wait_time = 600  # Maximum wait time in seconds
        end_time = time.time() + max_wait_time
        while time.time() < end_time:
            try:
                response = requests.get(url, headers=headers, verify=self.project_config_manager.get_certificate_path())
                response.raise_for_status()

                job_status = response.json()
                self.logger.debug(f"Job status: {job_status}")

                status = job_status.get('status',
                                        '').lower().strip()
                if status in XrayTestCaseUpload.JOB_STATUS_MAP:
                    status_text = XrayTestCaseUpload.JOB_STATUS_MAP.get(status)
                    robot_print_info(f"Bulk test import job status: {status_text}")
                else:
                    robot_print_info(f"Bulk test import job status: {status} (Unknown)")

                if status == 'successful':
                    uploaded_issues = self.extract_issue_id_key_from_result(job_status.get('result', {}))
                    break
                elif status == 'failed':
                    robot_print_error("Bulk test import failed.")
                    break
                elif status in ['pending', 'working']:
                    if time.time() < end_time:
                        num_test_cases = len(uploaded_issues)
                        if num_test_cases >= 100:
                            time.sleep(5)
                        elif num_test_cases >= 50:
                            time.sleep(4)
                        else:
                            time.sleep(3)
                    else:
                        robot_print_error("Bulk test import timed out after waiting for 600 seconds.")
                        break
                elif status in ['unsuccessful', 'partially_successful']:
                    self.logger.error(f"status to upload is unsuccessful")
                    break
                else:
                    self.logger.error(f"Unexpected job status: {status}")
                    break

            except requests.exceptions.RequestException as exp:
                robot_print_error(f"Error checking job status: {exp}")
                break

        return uploaded_issues

    def start_upload_test_case(self, test_sub_group, test_group, test_type):
        """
        Start the process of uploading test cases to Xray.
        Processes Robot Framework files, updates test types and scenarios in Xray, and initiates bulk upload of test cases.
        Args:
            test_sub_group (str): Test sub-group name.
            test_group (str): Test group name.
            test_type (str): Test case type.
        Returns: None
        """
        try:
            self.converter.process_robot_files(test_sub_group, test_group, test_type)
            issue_keys_with_prefix = self.converter.read_all_keys_from_excel()
            issue_keys = [key.replace("TEST_", "") for key in issue_keys_with_prefix]
            test_data_dict = self.jira_api_handler.fetch_test_data_from_jira(issue_keys=issue_keys,
                                                                             project_key=self.project_config_manager.get_project_test_case_key())
            file_path = self.converter.convert_to_json_format(test_group=test_group, test_sub_group=test_sub_group,
                                                              test_case_type=test_type)
            for key, value in test_data_dict.items():
                self.logger.debug(f"updating type and scenario for issue key: {key}")
                self.xray_api_handler.update_test_type_and_scenario(issue_key=key, issue_id=value.id)
            issue_links = self.converter.read_all_issue_links_from_excel()
            for issue_key, outward_issue_keys in issue_links:
                outward_issue_key_list = eval(outward_issue_keys)
                for outward_issue_key in outward_issue_key_list:
                    self.jira_api_handler.check_and_create_issue_link(issue_key, outward_issue_key.strip())
            if isinstance(file_path, list):
                if not file_path:
                    self.logger.info(f"No new test cases found to upload on JIRA")
                    return
                else:
                    raise ValueError(f"Expected a string for file_path, got a non-empty list: {file_path}")

            if not os.path.exists(file_path):
                self.logger.info(f"No new test cases found to upload on JIRA")
            else:
                with open(file_path, 'r') as file:
                    stored_json_data = json.load(file)
                if stored_json_data:
                    uploaded_issues = self.import_test_bulk(test_group=test_group, test_sub_group=test_sub_group,
                                                            test_type=test_type)
                    if uploaded_issues is not None:
                        for issue in uploaded_issues:
                            issue_key = issue['issue_key']
                            issue_id = issue['issue_id']
                            gherkin, test_type_name, summary = self.xray_api_handler.xray_get_issue_test(issue_id, issue_key)
                            test_data_dict[issue_key] = IssueTypeTestData(key=issue_key, id=issue_id, summary=summary,
                                                                          test_type=None)
                            self.converter.collect_robot_files(summary_name=summary, issue_key_value=issue_key)

            self.logger.debug(f"issuedIds: {[value.id for key, value in test_data_dict.items()]}")

        except IOError as exp:
            self.logger.error(f"Error to read the robot json report, EXCEPTION {exp}")
            return False
        except Exception as exp:
            robot_print_error(f"Error to upload X-Ray execution record, EXCEPTION: {exp}")
            return False
