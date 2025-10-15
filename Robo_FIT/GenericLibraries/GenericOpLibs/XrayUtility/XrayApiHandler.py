import json
import logging
from typing import Dict, Optional, Union

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import SSLError

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.JiraApiHandler import JiraApiHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.TcUpload.ConvertRobotToExcel import ConvertRobotToExcel
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger


class XrayApiHandler:
    """
    Handles interactions with the Xray API for fetching and updating test data.
    """
    __AUTH_URL = "https://xray.cloud.getxray.app/api/v1/authenticate"
    __XRAY_GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
    ISSUE_TYPE_TEST = "Test"
    CUCUMBER_TEST_TYPE = "Cucumber"
    MANUAL_TEST_TYPE = "Manual"
    GENERIC_TEST_TYPE = "Generic"

    # request methods
    __req_method_get = "GET"
    __req_method_post = "POST"
    __req_method_put = "PUT"
    __req_method_delete = "DELETE"

    def __init__(self):
        self.xray_auth = None
        self.project_config_manager = ProjectConfigManager()
        self.auth = None
        self.converter = ConvertRobotToExcel()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.jira_handler = JiraApiHandler()

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

    def __send_xray_request(self, url: str, method: str, headers: Dict, payload: Union[Dict, str, None] = None,
                            params: Union[Dict, None] = None, is_auth_request: bool =  False):
        try:
            if not is_auth_request:
                auth = self.get_user_auth(client_auth=self.project_config_manager.xray_client_info())
                if headers.get("Authorization") is None:
                    headers['Authorization'] = f'Bearer {auth}'

            if method == XrayApiHandler.__req_method_post or method == XrayApiHandler.__req_method_put:
                return requests.request(method,
                                        url,
                                        headers=headers,
                                        data=payload,
                                        verify=self.project_config_manager.get_certificate_path())
            elif method == XrayApiHandler.__req_method_get:
                return requests.request(method,
                                        url,
                                        headers=headers,
                                        params=params,
                                        verify=self.project_config_manager.get_certificate_path())
            else:
                raise ValueError(f"Given REST method '{method}' is not supported")
        except SSLError as exp:
            robot_print_error(f"CERTIFICATE_VERIFY_FAILED, EXCEPTION: {exp}")

    def get_user_auth(self, client_auth) -> str:
        """
        This function will authenticate the user
        :param client_auth: Client info like client_id and client_secret
        :type client_auth: String
        :return: Authentication token
        :rtype: String
        """
        if self.xray_auth is None:
            self.logger.debug(f"Certificate : {self.project_config_manager.get_certificate_path()}")
            auth_headers = {
                "Content-Type": "application/json",
            }
            response = self.__send_xray_request(url=XrayApiHandler.__AUTH_URL,
                                                method=XrayApiHandler.__req_method_post,
                                                headers=auth_headers,
                                                payload=client_auth,
                                                is_auth_request=True)
            self.xray_auth = response.text.replace('"', '')
        return self.xray_auth

    def execute_graphql_mutation(self, url: str, query: str) -> dict:
        """
        Executes a GraphQL mutation using HTTP POST.
        Args:
        - url (str): URL of the GraphQL endpoint.
        - query (str): GraphQL mutation query.
        Returns dict: Response data as dictionary.
        """
        client_info = self.project_config_manager.xray_client_info()
        auth = self.get_user_auth(client_auth=client_info)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {auth}'
        }
        try:
            data = {'query': query}
            response = self.__send_xray_request(url, method=XrayApiHandler.__req_method_post,
                                                headers=headers, payload=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Error executing GraphQL mutation: {e}")
            return {}

    def xray_get_issue_test(self, issue_id, issue_key):
        """
        Fetches test details from Xray using GraphQL.
        :param issue_id: Issue ID.
        :type issue_id: str
        :param issue_key: Issue Key.
        :return: Gherkin data, test type name, and summary if successful, otherwise None.
        :rtype: tuple
        """
        if not issue_id:
            self.logger.debug(f"Failed to extract issue ID from issue key: {issue_key}")
            return None, None, None
        get_test_query = """
        {
          getTest(issueId: "%s") {
            issueId
            gherkin
            testType {
                name
                kind
            }    
            jira(fields: ["key", "summary"])
          }
        }
        """ % issue_id

        try:
            response = self.execute_graphql_mutation(XrayApiHandler.__XRAY_GRAPHQL_URL, get_test_query)
            if response and 'data' in response and 'getTest' in response['data']:
                test_data = response['data']['getTest']
                if test_data is not None:
                    gherkin = test_data.get('gherkin', None)
                    test_type_name = test_data.get('testType', {}).get('name', None)
                    summary = test_data.get('jira', {}).get('summary', None)
                    return gherkin, test_type_name, summary
                else:
                    self.logger.info(f"No test data found for issue ID: {issue_key}")
            else:
                self.logger.info(f"Response data or 'getTest' key missing for issue ID: {issue_key}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching test data: {e}")
        return None, None, None

    def update_test_type(self, issue_key: str, issue_id, test_type: Optional[Dict[str, str]] = None) -> Dict:
        """
        Executes a GraphQL mutation to update the test type of issue in Jira.
        Default test_type is "Cucumber" if not provided.
        Args:
        - issue_key (str): Key of the issue to update.
        - test_type (Dict[str, str], optional): Dictionary containing updated test type information.
                                               Expected format: {"name": "Manual"} or {"name": "Automated"} etc.
        Returns Dict: Updated issue details if successful, empty dictionary otherwise.
        """
        if test_type is None:
            test_type = XrayApiHandler.CUCUMBER_TEST_TYPE

        try:
            if self.auth is None:
                self.auth = self.__create_auth()

            if not issue_id:
                self.logger.error(f"Failed to extract issue ID from issue key: {issue_key}")
                return {}
            mutation_query = f"""
                mutation {{
                    updateTestType(issueId: "{issue_id}", testType: {{name: "{test_type}"}}) {{
                        issueId
                        testType {{
                            name
                            kind
                        }}
                    }}
                }}
            """
            response = self.execute_graphql_mutation(XrayApiHandler.__XRAY_GRAPHQL_URL, mutation_query)
            if response.get("data") and response["data"].get("updateTestType"):
                return response["data"]["updateTestType"]
            else:
                self.logger.error(f"Failed to update test type for issue Key {issue_key}. Response: {response}")
                return {}

        except Exception as exp:
            robot_print_error(f"Exception occurred while updating test type for issue Key {issue_key}: {exp}")
            return {}

    def update_gherkin_test_definition(self, issue_key: str, issue_id):
        """
        Updates the Gherkin test definition for a given issue in Xray.
        :param issue_key: Key of the issue to update.
        :type issue_key: str
        :param issue_id: ID of the issue to update.
        :type issue_id: str
        :return: Updated issue details if successful, otherwise empty dictionary.
        :rtype: dict
        """
        try:
            if self.auth is None:
                self.auth = self.__create_auth()

            if not issue_id:
                self.logger.error(f"Failed to extract issue ID from issue key: {issue_id}")
                return {}

            gherkin_data = self.converter.read_gherkin_data_from_excel(issue_key)
            if not gherkin_data:
                self.logger.error(f"Failed to retrieve Gherkin data for issue key: {issue_key}")
                return {}

            mutation_query = f"""
                mutation {{
                    updateGherkinTestDefinition(issueId: "{issue_id}", gherkin: "{gherkin_data}") {{
                        issueId
                        gherkin
                    }}
                }}
            """
            response = self.execute_graphql_mutation(url=XrayApiHandler.__XRAY_GRAPHQL_URL, query=mutation_query)

            if response.get("data") and response["data"].get("updateGherkinTestDefinition"):
                return response["data"]["updateGherkinTestDefinition"]
            else:
                self.logger.error(
                    f"Failed to update Gherkin test definition for issue Key {issue_id}. Response: {response}")
                return {}

        except Exception as exp:
            robot_print_error(
                f"Exception occurred while updating Gherkin test definition for issue Key {issue_id}: {exp}")
            return {}

    def update_test_type_and_scenario(self, issue_key: str, issue_id):
        """
        Updates both the test type and the Gherkin test definition for a given issue.
        :param issue_key: The key of the issue to update.
        :param issue_id: The ID of the issue to update.
        """
        try:
            gherkin_data, test_type_name, summary = self.xray_get_issue_test(issue_id, issue_key)
            if test_type_name == "Cucumber":
                if gherkin_data is not None:
                    self.logger.info(f"Given test {issue_key} is in a valid Cucumber format")
                else:
                    self.update_gherkin_test_definition(issue_key, issue_id)
            elif test_type_name == "Manual":
                self.update_test_type(issue_key, issue_id)
                self.update_gherkin_test_definition(issue_key, issue_id)
            else:
                self.logger.info(f"Test type is neither 'Cucumber' nor 'Manual' for {issue_key}")
        except Exception as exp:
            robot_print_error(f"Exception encountered in update_test_type_and_scenario: {exp}")
