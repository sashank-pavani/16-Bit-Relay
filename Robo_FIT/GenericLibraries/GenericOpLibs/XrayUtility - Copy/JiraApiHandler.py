import json
import logging
from typing import Union, List, Dict, Tuple

import requests
from requests.auth import HTTPBasicAuth

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import TEST_CASE_TYPES, TEST_GROUPS, \
    TEST_SUB_GROUPS
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info, robot_print_error, \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger


class JiraApiHandler:
    # Issue Types
    ISSUE_TYPE_TEST = "Test"
    ISSUE_TYPE_TEST_EXECUTION = "Test Execution"

    # Transitions
    TRANS_DRAFT = "Draft"
    TRANS_DESIGN = "Design"
    TRANS_DESIGN_REVIEW = "Design Review"
    TRANS_IMPLEMENTATION = "Implementation"
    TRANS_IMPL_APPROVED = "Implementation Approved"
    TRANS_AUTOMATION_CONF = "Automation Confirmed"
    TRANS_FINAL_APPROVE = "Final Approval"
    TRANS_DROPPED = "Dropped"
    TRANS_REQUIRED_STATUS_RELEASED = "Released"
    TRANS_TE_IN_PROGRESS = "Set In Progress"
    TRANS_TE_DONE = "Set Done"

    # Issue state's
    __test_execution_status_in_progress = "In Progress"

    # Issue Creation
    ISSUE_CREATION_TE_REQUIRED_KNOWN_FIELDS = ["Issue Type", "Test Case Type", "Test Group", "Project", "Summary"]

    def __init__(self):
        self.project_config_manager = ProjectConfigManager()
        self.auth = None
        self.auth = self.__create_auth()
        self.issue_test_metadata = None
        self.issue_test_execution_metadata = None
        self.__allowed_transitions = self.__allowed_transitions_internal_record()
        self.logger = logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def __create_auth(self) -> HTTPBasicAuth:
        """
        This function create JIRA Auth
        :return: JIRA Auth
        :rtype: HTTPBasicAuth
        """
        if self.auth is None:
            self.auth = HTTPBasicAuth(self.project_config_manager.jira_user_email_id().replace('"', ""),
                                      str(self.project_config_manager.jira_api_token()).replace('"', ""))
        return self.auth

    def get_issue_by_summary(self, summary, issueType=ISSUE_TYPE_TEST):
        """
        This function is used to get the issue details base on summary of the test case.
        Test case summary should be matched with the Jira issue, and a project can be TE or TC.
        :param summary: Summary of the test case
        :type summary: String
        :param issueType: Issue type can be JiraApiHandler.ISSUE_TYPE_TEST or JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION
        :type issueType: String
        :return: Dict of Issue details if issue found else empty dict.
        :rtype: Dict
        """
        try:
            if self.auth is None:
                self.auth = self.__create_auth()

            headers = {
                "Accept": "application/json"
            }
            project_key = self.project_config_manager.get_project_test_case_key() if issueType == JiraApiHandler.ISSUE_TYPE_TEST else self.project_config_manager.get_project_test_execution_key()
            query = {
                'jql': f'issueType="{issueType}" AND summary ~ "{summary.strip()}" AND '
                       f'project={project_key}',
                'maxResults': 10000,
                'validateQuery': 'strict',
            }

            # self.logger.debug(f"Executing query as : {query}")

            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/search"
            response = requests.request(
                "GET",
                url,
                headers=headers,
                params=query,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                robot_print_info(f"Response = {response.content}")
                return response.json()
            else:
                robot_print_error(f"Error to get the issue: {response.content}")
                return {}
        except Exception as exp:
            robot_print_error(f"Error to get the issue: {summary}, EXCEPTION: {exp}")

    def update_custom_field_of_test_case(self, issue_ids, test_group, test_sub_group, test_type,
                                         project_key, build_version, issue_type=ISSUE_TYPE_TEST) -> bool:
        """
        Used to update the custom file of a test case.
        :return: True if successfully updated otherwise False
        :rtype: Bool
        """
        try:

            if self.auth is None:
                self.auth = self.__create_auth()
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            for issue_id in issue_ids:
                issue_data = self.get_issue_by_id_key(issue_id)
                if len(issue_data) == 0:
                    raise ValueError(f"No data found for issueId: {issue_id}")
                test_case_type_key = self.get_test_issue_field_id_by_name("Test Case Type", project_key)
                test_types = self.update_test_type(issue_data=issue_data, updated_test_case_type=test_type,
                                                   test_type_field_key=test_case_type_key)
                url = self.project_config_manager.jira_server_domain_url().replace('"', "")
                url = f"{url}/rest/api/3/issue/{issue_id}"
                payload_data = {'fields': {}}
                if issue_type == JiraApiHandler.ISSUE_TYPE_TEST:
                    test_case_type_key = self.get_test_issue_field_id_by_name("Test Case Type", project_key,
                                                                              issue_type=issue_type)
                    test_types = self.update_test_type(issue_data=issue_data, updated_test_case_type=test_type,
                                                       test_type_field_key=test_case_type_key)
                    payload_data['fields'][
                        self.get_test_issue_field_id_by_name("Planned Execution", project_key,
                                                             issue_type=issue_type)] = {
                        "value": "Automated"}
                    payload_data['fields'][
                        self.get_test_issue_field_id_by_name("Components", project_key, issue_type=issue_type)] = [
                        {"name": self.project_config_manager.jira_get_component_name()}]
                    payload_data['fields'][
                        self.get_test_issue_field_id_by_name("Test Group", project_key, issue_type=issue_type)] = {
                        "value": f"{test_group}",
                        "child": {"value": f"{test_sub_group}"}}
                    payload_data['fields'][test_case_type_key] = test_types
                elif issue_type == JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION:
                    payload_data['fields'][
                        self.get_test_issue_field_id_by_name("Actual Execution", project_key,
                                                             issue_type=issue_type)] = {
                        "value": "Automatically"}
                    payload_data['fields'][
                        self.get_test_issue_field_id_by_name("Components", project_key, issue_type=issue_type)] = [
                        {"name": self.project_config_manager.jira_get_component_name()}]
                    te_label = test_type.replace(" ", "_")
                    payload_data['fields']['labels'] = self.__update_labels(issue_data, f"{te_label.lower()}_TE")
                    if self.__is_valid_sw_version(build_version=build_version):
                        payload_data['fields'][
                            self.get_test_issue_field_id_by_name("SW Version", project_key,
                                                                 issue_type=issue_type)] = {"name": build_version}
                payload = json.dumps(payload_data)
                # self.logger.debug(f"url = {url} and payload: {payload}")
                response = requests.request(
                    "PUT",
                    url,
                    data=payload,
                    headers=headers,
                    auth=self.auth,
                    verify=False
                )
                if response.status_code == 204:
                    robot_print_info(f"204 No CONTENT, Custom fields updated for issues: {issue_id}")
                elif response.status_code == 400:
                    robot_print_error(
                        f"400 BAD REQUEST for issue Id: {issue_id}, RESPONSE = {response.text if response is not None else ''}")
                elif response.status_code == 403:
                    robot_print_error(
                        f"403 FORBIDDEN for issue Id: {issue_id} the request is not authenticated as "
                        f"the app that provided all the fields Please check configuration file")
                elif response.status_code == 404:
                    robot_print_error(
                        f"404 NOT FOUND for issue Id: {issue_id}: REASON: {response.content}")
                else:
                    robot_print_error(
                        f"Unknown response for issue Id: {issue_id} with status code: {response.status_code},  {response.content}")
                # update the transitions
                if issue_type == JiraApiHandler.ISSUE_TYPE_TEST:
                    self.set_transitions(issue_id=issue_id)
                if issue_type == JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION:
                    self.__set_te_transitions_to_in_progress(issue_id=issue_id)
        except Exception as exp:
            robot_print_error(f"Error to upload the custom field, EXCEPTION: {exp}")
            return False

    def update_test_type(self, issue_data, updated_test_case_type, test_type_field_key) -> List[Dict[str, str]]:
        """
        This function is used to update the test case type
        :param issue_data: Issue data comes from JIRA in dict format.
        :type issue_data: Dict
        :param updated_test_case_type: What value needs to be set for the test case
        :type updated_test_case_type: String
        :param test_type_field_key: Test case type filed key
        :type test_type_field_key: String
        :return: Updated Test case types value
        :rtype: List
        """
        try:
            if test_type_field_key in issue_data['fields']:
                if issue_data['fields'][test_type_field_key] is not None:
                    for test_types in issue_data['fields'][test_type_field_key]:
                        if test_types['value'] == updated_test_case_type:
                            return issue_data['fields'][test_type_field_key]
                    issue_data['fields'][test_type_field_key].append({"value": updated_test_case_type})
                    return issue_data['fields'][test_type_field_key]
                else:
                    issue_data['fields'][test_type_field_key] = [{"value": updated_test_case_type}]
                    return issue_data['fields'][test_type_field_key]
            else:
                robot_print_error(
                    f"No custom file test type for issue: {issue_data['key']}, custom field key: {test_type_field_key}")
        except KeyError as err:
            robot_print_error(f"Error to update custom field, EXCEPTION {err}")

    def __update_labels(self, issue_data, updated_label_value):
        try:
            if "labels" in issue_data["fields"]:
                labels = issue_data["fields"]["labels"]
                robot_print_info(f"Existing Labels for TE, {labels}")
                issue_data["fields"]["labels"].append(updated_label_value)
                return issue_data["fields"]["labels"]
        except KeyError as err:
            robot_print_error(f"Error to update the labels, EXCEPTION: {err}")

    def __is_valid_sw_version(self, build_version):
        try:
            if build_version is not None and build_version != "":
                robot_print_debug(f"Looking for {build_version} in valid SW versions")
                if build_version in self.__get_valid_sw_version_list():
                    return True
                else:
                    robot_print_error(f"Given software version: '{build_version}' is not in allowed version list")
                    return False
            else:
                raise ValueError("Build version value can't be None or empty")
        except Exception as exp:
            robot_print_error(f"Error to update the software version of issue, EXCEPTION: {exp}")
            return False

    def get_issue_by_id_key(self, issue_id_key):
        """
        This function will get the issue by using issue ID or Key
        :param issue_id_key: Key or ID of the issue
        :type issue_id_key: String
        :return: Issue details in dict format
        :rtype: Dict
        """
        try:
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue/{issue_id_key}"
            headers = {
                "Accept": "application/json"
            }
            if self.auth is None:
                self.auth = self.__create_auth()

            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                # self.logger.debug(f"get issue by id/key: {issue_id_key} RESPONSE = {response.json()}")
                return response.json()
            else:
                robot_print_error(f"Error to get the issue with Key: {issue_id_key}, RESPONSE: {response.content}")
                return {}
        except Exception as exp:
            robot_print_error(f"Error get the issue with id/key: {issue_id_key}, EXCEPTION: {exp}")

    def get_test_issue_field_id_by_name(self, field_name, project_key, issue_type=ISSUE_TYPE_TEST):
        """
        This function is used to get the Jira test case filed key/id by using filed names
        :param field_name: Name of the filed who's key user want to get
        :type field_name: String
        :param project_key: project key in which user want to get the filed key
        :type project_key: String
        :param issue_type: Issue type can be JiraApiHandler.ISSUE_TYPE_TEST or JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION
        :type issue_type: String
        :return: Field key
        :rtype: String
        """
        try:
            if issue_type == JiraApiHandler.ISSUE_TYPE_TEST:
                if self.issue_test_metadata is None:
                    self.issue_test_metadata = self.get_project_issue_test_metadata(project_key,
                                                                                    issue_jira_type=issue_type)
                # self.logger.debug(f"issue metadata => {self.issue_test_metadata}")
                for key, value in self.issue_test_metadata['fields'].items():
                    if value['name'] == field_name:
                        self.logger.debug(f" for field : {field_name} , key = {key}")
                        return key
            elif issue_type == JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION:
                if self.issue_test_execution_metadata is None:
                    self.issue_test_execution_metadata = self.get_project_issue_test_metadata(project_key,
                                                                                              issue_jira_type=issue_type)
                # self.logger.debug(f"issue metadata => {self.issue_test_execution_metadata}")
                for key, value in self.issue_test_execution_metadata['fields'].items():
                    if value['name'] == field_name:
                        self.logger.debug(f" for field : {field_name} , key = {key}")
                        return key
            # self.logger.debug(f"File: {field_name} is not found")
        except KeyError as exp:
            robot_print_error(f"Required value is not in issue metadata, EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(f"get_test_issue_field_id_by_name, EXCEPTION: {exp}")

    def get_project_issue_test_metadata(self, project_key, issue_jira_type=ISSUE_TYPE_TEST):
        """
        This function is used to get the metadata of the issue type. Like Test, Test Execution.
        :param project_key: Project key in which issue present.
        :type project_key: String
        :param issue_jira_type: Issue type can be JiraApiHandler.ISSUE_TYPE_TEST or JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION
        :type issue_jira_type: String
        :return: Dict format of the issue metadata
        :rtype: Dict
        """
        try:
            project_key = project_key.replace('"', '')
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            if issue_jira_type == JiraApiHandler.ISSUE_TYPE_TEST:
                # self.logger.debug(f"Getting metadata for : {issue_jira_type}")
                url = f"{url}/rest/api/3/issue/createmeta?projectKeys={project_key}&issuetype=Test&expand=projects.issuetypes.fields"
                # self.logger.debug(f"URL = {url}")
            elif issue_jira_type == JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION:
                # self.logger.debug(f"Getting metadata for : {issue_jira_type}")
                url = f"{url}/rest/api/3/issue/createmeta?projectKeys={project_key}&issuetype=\"Test Execution\"&expand=projects.issuetypes.fields"
                # self.logger.debug(f"URL = {url}")
            headers = {
                "Accept": "application/json"
            }
            if self.auth is None:
                self.auth = self.__create_auth()

            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                for issue in response.json()['projects']:
                    for issue_type in issue['issuetypes']:
                        if issue_type['name'] == issue_jira_type:
                            return issue_type
            else:
                robot_print_error(f"Can't get the metadat of issue, response code = {response.status_code},"
                                  f" content = {response.content}")
                return None
        except Exception as exp:
            robot_print_error(f"Error to get the metadata, EXCEPTION: {exp}")

    def __allowed_transitions_internal_record(self):
        """
        THis function will return the allowed transitions of the test case
        :return: Dict format of the allowed transition of test case
        :rtype: Dict
        """
        return {
            JiraApiHandler.ISSUE_TYPE_TEST: {
                "new": {
                    "allowed": ["Draft", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_DRAFT
                },
                "draft": {
                    "allowed": ["Design", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_DESIGN
                },
                "design": {
                    "allowed": ["Draft", "Design Review", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_DESIGN_REVIEW
                },
                "designReview": {
                    "allowed": ["Draft", "Implementation", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_IMPLEMENTATION
                },
                "implementation": {
                    "allowed": ["Draft", "Implementation Approved", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_IMPL_APPROVED
                },
                "implementationReview": {
                    "allowed": ["Draft", "Automation Confirmed", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_AUTOMATION_CONF
                },
                "automationDebug": {
                    "allowed": ["Draft", "Final Approval", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_FINAL_APPROVE
                },
                "release": {
                    "allowed": ["Draft", "Dropped"],
                    "nextTransition": JiraApiHandler.TRANS_FINAL_APPROVE
                }
            },
            JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION: {
                "New": {
                    "allowed": ["Invalid", "Set In Progress"],
                    "nextTransition": JiraApiHandler.TRANS_TE_IN_PROGRESS
                },
                "Set In Progress": {
                    "allowed": ["Set Done", "Invalid"],
                    "nextTransition": JiraApiHandler.TRANS_TE_DONE
                },
            }
        }

    def get_allowed_trans_by_jira(self, issue_id):
        """
        THis function is used to get the allowed transition of the test case. Base on the issue id it will check on the
        jira and see what is the next allowed transitions of the test case.
        :param issue_id: Issue id/key
        :type issue_id: String
        :return: Allowed transitions in dict format id response status code == 200 else None
        :rtype: Dict
        """
        try:
            if self.auth is None:
                self.auth = self.__create_auth()
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue/{issue_id}/transitions"
            headers = {
                "Accept": "application/json"
            }
            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                return response.json()["transitions"]
            elif response.status_code == 400:
                robot_print_error(f"400 Unauthorized: "
                                  f"the authentication credentials are incorrect or missing.")
            elif response.status_code == 404:
                robot_print_error(f"404 Not Found: "
                                  f"the issue: {issue_id} is not found or the user does not have permission to view it.")
            else:
                robot_print_error(f"Unknown response for issue id = {issue_id}, "
                                  f"RESPONSE: {response.content}")
        except Exception as exp:
            robot_print_error(f"Error to get the Transition, EXCEPTION: {exp}")

    def __get_next_transition_id(self, issue_id, current_status, issue_type) -> Union[str, None]:
        """
        This function will get the next allowed transition base on the current status
        :param issue_id: Issue id of the test case
        :type issue_id: String
        :param current_status: Current status of the test case
        :type current_status: String
        :return: None
        :rtype: None
        """
        jira_allowed_trans = self.get_allowed_trans_by_jira(issue_id)
        # self.logger.debug(f"Allowed Transition Id for issue type: '{issue_type}' and issue_id: {issue_id} is '{jira_allowed_trans}'")
        if jira_allowed_trans:
            if current_status in self.__allowed_transitions[issue_type].keys():
                for allowed_trans in jira_allowed_trans:
                    if self.__allowed_transitions[issue_type][current_status]['nextTransition'] == allowed_trans[
                        'name']:
                        return str(allowed_trans['id'])
            else:
                robot_print_error(f"Invalid Transition status = {current_status}")
        else:
            robot_print_error(f"Error to get the jira allowed transition, please check the logs for more info.")

    def set_transition_on_jira(self, trans_id: str, issue_id) -> bool:
        """
        This function is set the transition on the jira.
        :param trans_id: Transition id
        :type trans_id: String
        :param issue_id: Issue ID/key of the test case
        :type issue_id: String
        :return: True if success, else False
        :rtype: bool
        """
        try:
            if trans_id is None and trans_id == "":
                raise ValueError(f"Invalid transition id : {trans_id} for issue id: {issue_id}")
            # self.logger.debug(f"Setting the transition : {trans_id} for issue: {issue_id}")
            if self.auth is None:
                self.auth = self.__create_auth()
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue/{issue_id}/transitions"
            payload = json.dumps({
                "transition": {
                    "id": trans_id
                },
            })

            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=headers,
                auth=self.auth,
                verify=False)

            if response.status_code == 204:
                robot_print_info(f"Set the transition: {trans_id} for issue: {issue_id} is done")
                return True
            elif response.status_code == 400:
                robot_print_error(f"400 Bad Request: RETURN IF: ")
                robot_print_error("""1. no transition is specified.\n
                    2. the user does not have permission to transition the issue.\n
                    3. a field that isn't included on the transition screen is defined in "fields" or "update".\n
                    4. a field is specified in both "fields" and "update."\n
                    5. the request is invalid for any other reason.\n""")
                return False
            elif response.status_code == 401:
                robot_print_error(f"400 Unauthorized: "
                                  f"the authentication credentials are incorrect or missing.")
                return False
            elif response.status_code == 404:
                robot_print_error(f"404 Not Found: "
                                  f"the issue: {issue_id} is not found or the user does not have permission to view it.")
                return False
            else:
                robot_print_error(f"Unknown response for issue id = {issue_id}, "
                                  f"RESPONSE: {response.content}")
                return False

        except Exception as exp:
            robot_print_error(f"Error to set the transition : {trans_id}, on JIRA, EXCEPTION: {exp}")
            return False

    def get_current_status_of_issue(self, issue_id):
        """
        This function will return the current status of the issue base on issue id/key
        :param issue_id: Issue id or key
        :type issue_id: String
        :return: current status of the test case
        :rtype: String
        """
        current_status = self.get_issue_by_id_key(issue_id)
        if len(current_status) == 0:
            raise ValueError(f"Invalid issue id : {issue_id}, Please check the logs for more details")
        current_status = current_status['fields']['status']['name']
        # self.logger.debug(f"Issue: {issue_id} current status = {current_status}")
        return current_status

    def __set_te_transitions_to_in_progress(self, issue_id):
        try:
            # self.logger.debug(f"Setting transition of issue: '{issue_id}' to in-progress")
            current_state = self.get_current_status_of_issue(issue_id)
            # self.logger.debug(f"Issue id: {issue_id} current state: '{current_state}'")
            if current_state == JiraApiHandler.__test_execution_status_in_progress:
                self.logger.debug(f"Issue: '{issue_id}' state already in 'In Progress'")
            else:
                trans_id = self.__get_next_transition_id(issue_id, current_state,
                                                         issue_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION)
                self.set_transition_on_jira(trans_id, issue_id)
        except Exception as exp:
            self.logger.error(f"Error to set the TE transition, EXCEPTION: {exp}")

    def set_transitions(self, issue_id, transition=TRANS_REQUIRED_STATUS_RELEASED):
        """
        This function set the current status of the issue test case to give transition
        :param issue_id: Issue Id or key of the test case
        :type issue_id: String
        :param transition: Transition value which user wants to set, default is JiraApiHandler.TRANS_REQUIRED_STATUS_RELEASED
        :type transition: String
        :return: None
        :rtype: None
        """
        try:
            current_status = ""
            num_try = 0
            current_status = self.get_current_status_of_issue(issue_id)
            # self.logger.debug(f"Current status = {current_status}, "
            #                   f"{'setting the transitions' if current_status != transition else 'already in transition'}")
            # self.logger.debug(f"User want to set the transition to : {transition}")
            while current_status != transition and num_try < 10:
                current_status = "".join(
                    [x.lower() if current_status.split(" ").index(x) == 0 else x.title() for x in
                     current_status.split(" ")])
                # self.logger.debug(f"Current status = {current_status}")
                trans_id = self.__get_next_transition_id(issue_id, current_status,
                                                         issue_type=JiraApiHandler.ISSUE_TYPE_TEST)
                self.set_transition_on_jira(trans_id, issue_id)
                num_try += 1
                current_status = self.get_current_status_of_issue(issue_id)
            if num_try == 10:
                robot_print_error(f"It seems we have tried to change the transition but not able to set it to"
                                  f" {transition}. Please check the logs for more info")
        except Exception as exp:
            robot_print_error(f"Error to set the issue: {issue_id} transition to : {transition},"
                              f"EXCEPTION: {exp} ")

    def __get_valid_sw_version_list(self) -> List:
        try:
            fields = self.issue_test_execution_metadata["fields"]
            # self.logger.debug(f"Fields  = {fields}")
            if self.issue_test_execution_metadata is None:
                self.issue_test_execution_metadata = self.get_project_issue_test_metadata(
                    project_key=self.project_config_manager.get_project_test_execution_key(),
                    issue_jira_type=JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION)
            allow_versions = []
            is_found = False
            for key, value in self.issue_test_execution_metadata["fields"].items():
                if is_found:
                    break
                # self.logger.debug(f"Value = {value}")
                if value['name'] == "SW Version":
                    is_found = True
                    # self.logger.debug(f"'SW Version' field custom key is = {key}")
                    for all_versions in value["allowedValues"]:
                        self.logger.debug(f"Adding value = {all_versions['name']}")
                        allow_versions.append(all_versions['name'])
            # self.logger.debug(f"Allowed SW versions are: {allow_versions}")
            return allow_versions
        except Exception as exp:
            self.logger.debug(
                f"Error to get the allowed SW version, so can't update 'SW Version' field, EXCEPTION: {exp}")

    def get_given_project_issue_types(self, project_key: str) -> List[Tuple[str, str]]:
        """
        This function will get the given project ``project_key`` supported project types.
        For Example:

        TE project only supports Test Plan, a Test Execution
        TC project only supports a Test case, Preconditions, etc.

        :param project_key: Key of the project which data user wants to check
        :type project_key: str
        :return: List of tuple of a supported project key, name

            For example: [(12321, "Test Execution"), (12223, "Test Plan")]

        :rtype: List[Tuple[str, str]]
        """
        try:

            def get_issue_id_name_from_response(res) -> List[Tuple[str, str]]:
                """
                Parse the response and get ID and NAME,
                :param res: Response of the parent API
                :type res: dict
                :return: List[Tuple[ID, NAME]]
                :rtype: List[Tuple[str, str]]
                """
                try:
                    data = []
                    for issue_data in res['issueTypes']:
                        data.append((issue_data['id'], issue_data['name']))
                    return data
                except Exception as exp:
                    robot_print_error(f"Error to get the issue ID and name from the repose, EXCEPTION: {exp}")

            if self.auth is None:
                self.auth = self.__create_auth()
            headers = {
                "Accept": "application/json"
            }
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue/createmeta/{project_key}/issuetypes"
            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                return get_issue_id_name_from_response(response.json())
            elif response.status_code == 400:
                robot_print_error(f"BAD REQUEST: Given request for getting issue types of project='{project_key}' "
                                  f"is invalid request, status code = 400")
            elif response.status_code == 401:
                robot_print_error(f"Unauthorized: authentication credentials are incorrect or missing, "
                                  f"status code = 401")
            else:
                robot_print_error(f"Invalid response for getting issue type of project='{project_key}',"
                                  f"status code = {response.status_code}")
        except Exception as exp:
            robot_print_error(f"Error to get the issue type of given project='{project_key}',"
                              f"EXCEPTION: {exp}")

    def get_required_fields_for_issue_creation(self, project_key: str, issue_type_id: str) -> List[Tuple[str, str]]:
        """
        This function will provide the required fields list for creating a given issue `issue_type_id`
        :param project_key: Project key where user wants to create an issue
        :type project_key: str
        :param issue_type_id: Issue Type id, for example, Test Plan, Test Case etc. has one unique id on Jira for peroject.
        :type issue_type_id: str
        :return: List of tuple of issue field key and Name.
        :rtype: List[Tuple[str, str]]
        """
        try:
            def parse_response(res: dict):
                """
                Function parse the response and get the required data i.e list of tuple of issue field key and Name.
                :param res: Response of the parent function.
                :type res: dict
                :return: list of tuple of issue field key and Name.
                :rtype: List[Tuple[str, str]]:
                """
                required_values = []
                for data in res["fields"]:
                    if data.get("required") is not None:
                        if data["required"]:
                            required_values.append((data["key"], data['name']))
                return required_values

            if self.auth is None:
                self.auth = self.__create_auth()
            headers = {
                "Accept": "application/json"
            }
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue/createmeta/{project_key}/issuetypes/{issue_type_id}"
            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 200:
                return parse_response(response.json())
            elif response.status_code == 400:
                robot_print_error(
                    f"BAD REQUEST: Given request for getting issue required files of project='{project_key}' "
                    f" and {issue_type_id=} is invalid request, status code = 400")
            elif response.status_code == 401:
                robot_print_error(f"Unauthorized: authentication credentials are incorrect or missing, "
                                  f"status code = 401")
            else:
                robot_print_error(
                    f"Invalid response for getting issue metadata of project='{project_key}' and {issue_type_id=},"
                    f"status code = {response.status_code}")
        except Exception as exp:
            robot_print_error(f"Error to get the issue required files for {project_key=} & {issue_type_id=}, "
                              f"EXCEPTION: {exp}")

    def create_issue_on_jira(self, project_key, test_case_type: str, test_group: str, test_sub_group: str,
                             summary: str, issue_type=ISSUE_TYPE_TEST_EXECUTION):
        f"""
        This function will create the issue of type `issue_type`. Currently, function support only issue creation of 
        Test Case and Test Execution.
        :param project_key: Project key where user wants to create the issue
        :type project_key: str
        :param test_case_type: Type of the test cases i.e. {TEST_CASE_TYPES}
        :type test_case_type: str
        :param test_group: Test Group value, i.e. {TEST_GROUPS}
        :type test_group: str
        :param test_sub_group: Test Sub group types i.e {TEST_SUB_GROUPS}
        :type test_sub_group: str
        :param summary: Summary of the Issue
        :type summary: str
        :param issue_type: Type of the issue i.e {JiraApiHandler.ISSUE_TYPE_TEST} or 
            {JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION}.
            (Default) {JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION}
        :type issue_type: str
        :return: Key of the newly created issue if created successfully else False
        :rtype: Union[str, bool]
        """
        try:
            # ID of the issue supported in a given project key,
            # for example, Test Plan, Test Execution, etc.
            project_issue_id = None
            issue_types_data = self.get_given_project_issue_types(project_key)
            for issue_type_data in issue_types_data:
                if issue_type_data[1] == issue_type:
                    project_issue_id = issue_type_data[0]
            if project_issue_id is not None:
                required_fields = self.get_required_fields_for_issue_creation(
                    project_key=project_key,
                    issue_type_id=project_issue_id
                )
                if len(required_fields) > 0:
                    if len(required_fields) == len(JiraApiHandler.ISSUE_CREATION_TE_REQUIRED_KNOWN_FIELDS):
                        issue_creation_data = self.get_issue_creation_data(required_fields=required_fields,
                                                                           test_case_type=test_case_type,
                                                                           test_group=test_group,
                                                                           test_sub_group=test_sub_group,
                                                                           summary=summary,
                                                                           issue_type=issue_type)
                        return self.__create_issue_on_jira(issue_creation_data=issue_creation_data)
                    else:
                        raise ValueError(f"It seems known required fields are "
                                         f"'{JiraApiHandler.ISSUE_CREATION_TE_REQUIRED_KNOWN_FIELDS}', but JIRA "
                                         f"required '{required_fields}', Please reach out to ROBOFIT Dev team or "
                                         f"raise a defect on "
                                         f"https://visteon.atlassian.net/jira/software/c/projects/CDCINTTION/boards/677")
                else:
                    raise ValueError(f"It seems no required files for the given {project_key = } & {issue_type = },"
                                     f"{required_fields = }")
            else:
                raise ValueError(f"There is not issue type '{issue_type}' available in '{issue_types_data}'")
        except Exception as exp:
            robot_print_error(f"Error to create the issue on JIRA, EXCEPTION: {exp}")

    def get_issue_creation_data(self, required_fields, test_case_type: str, test_group: str, test_sub_group: str,
                                summary, issue_type=ISSUE_TYPE_TEST_EXECUTION) -> Dict:
        f"""
        This function will get the issue creation data. This function creates what all the data is
          required for creating a new issue. 
        :param required_fields: Required fields that come from Jira after calling ``get_required_fields_for_issue_creation()``.
        :type required_fields: dict
        :param test_case_type: Type of the test cases i.e. {TEST_CASE_TYPES}
        :type test_case_type: str
        :param test_group: Test Group value, i.e. {TEST_GROUPS}
        :type test_group: str
        :param test_sub_group: Test Sub group types i.e {TEST_SUB_GROUPS}
        :type test_sub_group: str
        :param summary: Summary of the Issue
        :type summary: str
        :param issue_type: Type of the issue i.e {JiraApiHandler.ISSUE_TYPE_TEST} or 
            {JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION}.
            (Default) {JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION}
        :type issue_type: str
        :return: Dictionary of the required data
        :rtype: Dict
        """
        try:
            fields = {'fields': {}}
            fields['fields']['assignee'] = self.project_config_manager.jira_user_id()
            fields['fields']['components'] = [{"name": self.project_config_manager.jira_get_component_name()}]
            for required_field in required_fields:
                # [('customfield_10431', 'Test Case Type'), ('customfield_10469', 'Test Group'), ('issuetype', 'Issue Type'), ('project', 'Project'), ('summary', 'Summary')]
                if "Test Case Type" == required_field[1]:
                    fields['fields'][required_field[0]] = [{"value": test_case_type}]
                if "Test Group" == required_field[1]:
                    fields['fields'][required_field[0]] = {
                        "child": {
                            "value": test_sub_group
                        },
                        "value": test_group
                    }
                if "Issue Type" == required_field[1]:
                    fields['fields'][required_field[0]] = {
                        "name": issue_type
                    }
                if "Project" == required_field[1]:
                    fields['fields'][required_field[0]] = {
                        "key": self.project_config_manager.get_project_test_execution_key() if issue_type == JiraApiHandler.ISSUE_TYPE_TEST_EXECUTION else self.project_config_manager.get_project_test_case_key()
                    }
                if "Summary" == required_field[1]:
                    fields["fields"][required_field[0]] = summary
            if len(fields['fields']) > 2:
                return fields
            else:
                raise ValueError("Error to create the issue data for creating issue on Jira, "
                                 f"{fields = }")
        except Exception as exp:
            robot_print_error(f"Error to get issue creation data, EXCEPTION: {exp}")

    def __create_issue_on_jira(self, issue_creation_data: Dict) -> Union[str, bool]:
        """
        This function will create the issue on Jira by calling the jira api and provide the given
        ``issue_creation_data``.
        :param issue_creation_data: Final data which is required to create the issue on jira.
        :type issue_creation_data: dict
        :return: New created issue key as string if successfully created else False
        :rtype: Union[str, bool]
        """
        try:
            if self.auth is None:
                self.auth = self.__create_auth()
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            url = self.project_config_manager.jira_server_domain_url().replace('"', "")
            url = f"{url}/rest/api/3/issue"
            payload = json.dumps(issue_creation_data)

            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=headers,
                auth=self.auth,
                verify=False
            )
            if response.status_code == 201:
                robot_print_info(f"Issue created with {response.json()}")
                return response.json()['key']
            elif response.status_code == 400:
                robot_print_error(f"""Returned if the request:
                        1. is missing required fields.
                        2. contains invalid field values.
                        3. contains fields that cannot be set for the issue type.
                        4. is by a user who does not have the necessary permission.
                        5. is to create a subtype in a project different that of the parent issue.
                        6. is for a subtask when the option to create subtasks is disabled.
                        7. is invalid for any other reason.
                        {response.text}""")
                return False
            elif response.status_code == 401:
                robot_print_error(f"Unauthorized: authentication credentials are incorrect or missing, "
                                  f"status code = 401, {response.text}")
                return False
            elif response.status_code == 403:
                robot_print_error(f"Forbidden: the user does not have the necessary permission to create the issue on "
                                  f"Jira, {response.text}")
                return False
            elif response.status_code == 422:
                robot_print_error(f"Unprocessable Entity:  configuration problem prevents the creation of the issue."
                                  f" {response.text}")
                return False
            else:
                robot_print_error(
                    f"Invalid response for while creating issue"
                    f"status code = {response.status_code}, {response.text}")
                return False
        except Exception as exp:
            robot_print_error(f"Error to create the issue on Jira for {issue_creation_data = },"
                              f" EXCEPTION: {exp}")
            return False
