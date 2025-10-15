import json
import math
import os
from pathlib import Path
from typing import List
import pandas as pd
import logging
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, ROBOT_SCRIPTS, \
    ROBOT_SCRIPTS_DIR_NAME, ROBOFIT_XRAY_UTILITY_EXCEL_FILE_NAME, ROBOFIT_XRAY_UTILITY_EXCEL_FILE_TEMP_NAME, \
    ROBOFIT_NEW_TC_JSON_FILE_NAME, TEST_GROUPS, TEST_SUB_GROUPS, TEST_CASE_TYPES, TEAM_SWE5, TEST_CASES
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility.JiraApiHandler import JiraApiHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.XrayUtility import logger


class ConvertRobotToExcel:
    __test_issue_metadata = None

    def __init__(self):
        self.df = None
        self.project_config_manager = ProjectConfigManager()
        self.common_keywords = CommonKeywordsClass()
        self.__get_test_issue_metadata()
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def get_excel_file_path(self):
        """Return the path to the Excel file."""
        return Path(str(os.path.join(self.common_keywords.get_xray_utility_logs_dir_path(),
                                     ROBOFIT_XRAY_UTILITY_EXCEL_FILE_NAME)))

    @property
    def __get_excel_temp_path(self):
        """Return the path to the temporary Excel file."""
        return Path(str(os.path.join(self.common_keywords.get_xray_utility_logs_dir_path(),
                                     ROBOFIT_XRAY_UTILITY_EXCEL_FILE_TEMP_NAME)))

    def get_json_file_path(self):
        """Return the path to the JSON file."""
        return Path(str(os.path.join(self.common_keywords.get_xray_utility_logs_dir_path(),
                                     ROBOFIT_NEW_TC_JSON_FILE_NAME)))

    def __get_test_issue_metadata(self):
        """Retrieve the metadata for test issues if not already set."""
        if ConvertRobotToExcel.__test_issue_metadata is None:
            self.__set_test_issue_metadata()
        return ConvertRobotToExcel.__test_issue_metadata

    def __set_test_issue_metadata(self):
        """Set the metadata for test issues by fetching it from JIRA."""
        try:
            ConvertRobotToExcel.__test_issue_metadata = JiraApiHandler().get_project_issue_test_metadata(
                project_key=self.project_config_manager.get_project_test_case_key(),
                issue_jira_type=JiraApiHandler.ISSUE_TYPE_TEST
            )
        except Exception as exp:
            robot_print_error(f"Error to set the issue metadata, EXCEPTION: {exp}")

    def find_robot_files(self):
        """Find all .robot files in the given directory, excluding '__init__.robot'.
        The method traverses the directory structure starting from the root path, looking for directories
        and collecting paths to .robot files.
        Returns dict: A dictionary where keys are directory names and values are lists of .robot file paths within those directories.
        Raises NotADirectoryError: If the script path does not exist or is not a directory.
        """
        try:
            robot_files = {}
            script_path = os.path.join(self.common_keywords.get_root_path(), PROJECT, ROBOT_SCRIPTS, ROBOT_SCRIPTS_DIR_NAME)
            if not os.path.isdir(script_path):
                script_path = os.path.join(self.common_keywords.get_root_path(), PROJECT, TEAM_SWE5, TEST_CASES)
            for item in os.listdir(script_path):
                item_path = os.path.join(script_path, item)
                if os.path.isdir(item_path):
                    robot_files[item] = []
                    for dir_path, _, filenames in os.walk(item_path):
                        for filename in filenames:
                            if ConvertRobotToExcel.should_include_robot_file(filename):
                                robot_files[item].append(os.path.join(dir_path, filename))
            return robot_files
        except Exception as exp:
            robot_print_error(f"Error to find robot files, EXCEPTION: {exp}")

    def get_custom_field_key(self, field_name: str):
        """Retrieve the key for a custom field in the test issue metadata.
        Args:
            field_name (str): The name of the custom field to look up.
        Returns str: The key corresponding to the custom field name.
        Raises ValueError: If the given field name is not valid for the issue type 'Test case'.
        """
        try:
            if ConvertRobotToExcel.__test_issue_metadata is None:
                ConvertRobotToExcel.__test_issue_metadata = self.__get_test_issue_metadata()
            for key, value in ConvertRobotToExcel.__test_issue_metadata['fields'].items():
                if value['name'] == field_name:
                    return key
            raise ValueError(f"Given field '{field_name}' for issue type 'Test case' is not valid, "
                             f"Kindly use the valid test case field")
        except Exception as exp:
            robot_print_error(f"Error to get custom field key, EXCEPTION: {exp}")

    @staticmethod
    def should_include_robot_file(filename):
        """Check if the given filename should be included."""
        return filename.endswith('.robot') and filename != '__init__.robot' and "keywords" not in filename.lower()

    def get_required_fields_of_test_case(self, test_case, test_sub_group, test_group, test_case_type):
        """Construct the required fields for a test case in the format required by JIRA.
        This method extracts necessary information from the given test case and prepares a dictionary with the required
        fields formatted for JIRA.
        Args:
            test_case (dict): A dictionary containing the test case details.
            test_sub_group (str): The subgroup to which the test case belongs.
            test_group (str): The group to which the test case belongs.
            test_case_type (str): The type of the test case.
        Returns dict: A dictionary containing the required fields formatted for JIRA.
        """
        try:
            tc_summary = test_case['summary']
            tc_labels = test_case['labels']
            if isinstance(tc_labels, str):
                tc_labels = eval(tc_labels)
            feature_group = test_case['Feature Group']
            fields = {'summary': tc_summary,
                      'project': {
                          'key': self.project_config_manager.get_project_test_case_key()
                      },
                      "labels": tc_labels,
                      f"{self.get_custom_field_key(field_name='Test Group')}": {
                          "child": {
                              "value": test_sub_group
                          },
                          "value": test_group
                      },
                      f"{self.get_custom_field_key(field_name='Test Case Type')}": [{"value": test_case_type}],
                      f"{self.get_custom_field_key(field_name='Components')}": [
                          {"name": self.project_config_manager.jira_get_component_name()}]
                      }
            return fields
        except Exception as exp:
            robot_print_error(f"Error to get required field for the test case, EXCEPTION: {exp}")

    def __parse_robot_file(self, robot_file, suite_name, feature_group):
        """
        Parse the .robot file and extract test cases.
        Args:
            robot_file (str): Path to the .robot file to parse.
            suite_name (str): Name of the test suite to assign to extracted test cases.
            feature_group (str): Name of the feature group to assign to extracted test cases.
        Returns list: List of dictionaries, each representing a test case with keys 'key', 'summary', 'gherkin_def',
        'labels', 'Suite', and 'Feature Group'.
        """
        try:
            test_cases = []
            current_test_case = None
            tag_key = self.project_config_manager.get_project_test_case_key()
            skip_lines_prefixes = ['#', '*', 'Resource', 'Variables', 'Suite Setup',
                                   'Test Setup', 'Test Teardown', 'Suite Teardown', 'Library', 'User Suite Setup',
                                   'User Suite Teardown', 'User Test Setup', 'User Test Teardown']

            with open(robot_file, 'r') as file:
                for line in file:
                    line = line.rstrip()

                    if line.startswith(tuple(skip_lines_prefixes)) or line == '':
                        continue

                    if line.startswith(" ") or line.startswith("\t"):
                        if current_test_case is None:
                            continue

                        if line.strip().startswith('[Tags]'):
                            tags = line.strip().split()[1:]
                            labels = []
                            for tag in tags:
                                if tag_key in tag:
                                    current_test_case['key'] = tag
                                else:
                                    labels.append(tag)
                            current_test_case['labels'] = labels
                        elif line.strip().startswith('[Documentation]'):
                            doc_info = line.strip().split()[1:]
                            issue_links = []
                            for issue in doc_info:
                                if issue.startswith("REQ_"):
                                    issue_links.append(issue[4:])
                            current_test_case['issue_links'] = issue_links
                        elif line.strip().startswith(('Given', 'When', 'Then', 'And')):
                            if current_test_case:
                                if current_test_case['gherkin_def']:
                                    current_test_case['gherkin_def'] += '\n'
                                current_test_case['gherkin_def'] += line.strip()
                    else:
                        if current_test_case:
                            test_cases.append(current_test_case)

                        current_test_case = {'key': 'NA', 'summary': '', 'gherkin_def': '',
                                             'labels': [], 'Suite': suite_name, 'Feature Group': feature_group}

                        if line.startswith(tag_key):
                            parts = line.split(maxsplit=1)
                            if len(parts) > 1:
                                current_test_case['key'] = parts[0]
                                current_test_case['summary'] = parts[1]
                            else:
                                current_test_case['key'] = 'NA'
                                current_test_case['summary'] = line.strip()
                        else:
                            current_test_case['key'] = 'NA'
                            current_test_case['summary'] = line.strip()

                if current_test_case:
                    test_cases.append(current_test_case)

            return test_cases
        except Exception as exp:
            robot_print_error(f"Error to parse robot file, EXCEPTION: {exp}")

    @staticmethod
    def __default_df():
        """
        Create a default DataFrame for 'Test Group', 'Test Sub Group', and 'Test Case Type'.
        Returns pandas.DataFrame: DataFrame with default values for 'Test Group', 'Test Sub Group', and 'Test Case Type'.
        """
        test_group_list = ['Select the Value'] + list(TEST_GROUPS.values())
        test_sub_group_list = ['Select the Value'] + list(TEST_SUB_GROUPS.values())
        test_case_type_list = ['Select the Value'] + list(TEST_CASE_TYPES.values())
        test_group_list.extend([''] * (
                max(len(test_group_list), len(test_sub_group_list), len(test_case_type_list)) - len(test_group_list)))
        test_sub_group_list.extend([''] * (
                max(len(test_group_list), len(test_sub_group_list), len(test_case_type_list)) - len(test_sub_group_list)))
        test_case_type_list.extend([''] * (
                max(len(test_group_list), len(test_sub_group_list), len(test_case_type_list)) - len(test_case_type_list)))
        data_set = {
            "Test Group": test_group_list,
            "Test Sub Group": test_sub_group_list,
            "Test Case Type": test_case_type_list,
        }
        return pd.DataFrame(data_set)

    def __write_to_excel_new(self, test_cases: List, test_sub_group, test_group, test_type):
        """Write the test cases to an Excel file in a structured format.
        This method takes a list of test cases and writes their details into an Excel file.
        Args:
            test_cases (List): A list of dictionaries, each containing details of a test case.
            test_sub_group (str): The subgroup to which the test cases belong.
            test_group (str): The group to which the test cases belong.
            test_type (str): The type of the test cases.
        Raises pd.errors.EmptyDataError: If the data frame is empty and there are issues with converting .robot scripts to Excel.
        """
        try:
            headers = ['key', 'summary', 'gherkin_def', 'labels', 'Suite', 'Feature Group', "Test Group",
                       "Test Sub Group", "Test Case Type", "Issue Links"]
            data_set = {'key': [],
                        'summary': [], 'gherkin_def': [], 'labels': [], 'Suite': [], 'Feature Group': [], "Test Group": [],
                        "Test Sub Group": [], "Test Case Type": [], "Issue Links": []}
            for test_case in test_cases:
                data_set['key'].append(test_case['key'])
                data_set['summary'].append(test_case['summary'])
                data_set['gherkin_def'].append(test_case['gherkin_def'])
                data_set['labels'].append(test_case['labels'])
                data_set['Suite'].append(test_case['Suite'])
                data_set['Feature Group'].append(test_case['Feature Group'])
                data_set['Test Group'].append(test_group)
                data_set['Test Sub Group'].append(test_sub_group)
                data_set['Test Case Type'].append(test_type)
                if 'issue_links' in test_case:
                    data_set['Issue Links'].append(test_case['issue_links'])
                else:
                    data_set['Issue Links'].append('')
            df = pd.DataFrame(data_set)
            if not df.empty:
                df.to_excel(self.__get_excel_temp_path, index=False)
                df1 = pd.read_excel(self.__get_excel_temp_path)
                writer = pd.ExcelWriter(
                    self.get_excel_file_path,
                    engine='xlsxwriter')
                df1.to_excel(writer, sheet_name="Sheet1", index=False)
                df2 = ConvertRobotToExcel.__default_df()
                df2.to_excel(writer, sheet_name="Data", index=False)
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                data_worksheet = writer.sheets['Data']
                for i in range(2, len(data_set['key'])):
                    worksheet.data_validation(f'G{i}', {'validate': 'list',
                                                        'source': "='Data'!$A$2:$A$6"})
                    worksheet.data_validation(f'H{i}', {'validate': 'list',
                                                        'source': "='Data'!$B$2:$B$15"})
                    worksheet.data_validation(f'I{i}', {'validate': 'list',
                                                        'source': "='Data'!$C$2:$C$24"})
                writer.close()
                os.remove(self.__get_excel_temp_path)
            else:
                self.logger.error(f"data frame is empty = {df}")
                raise pd.errors.EmptyDataError("Some issue with converting .robot scripts to excel, Please check the logs")
        except Exception as exp:
            robot_print_error(f"Error to write test cases to excel, EXCEPTION: {exp}")

    @staticmethod
    def map_feature_group_name(original_name):
        """Map original feature group name to standardized feature group name."""
        feature_group_mapping = {
            'AndroidAuto': 'Android_Auto',
            'Bluetooth': 'Bluetooth',
            'CarPlay': 'Phone_Projection',
            'CrossPlatform': 'Platform_Configuration',
            'ETM': 'Logger',
            'Flashing': 'HMI',
            'Home': 'HMI',
            'Media': 'Media',
            'Navigation': 'Navigation',
            'Performance': 'KPI_Performanence',
            'PlatformHealthTable': 'CCCM_Health_Monitor',
            'PowerCycle': 'Power',
            'Settings': 'Settings',
            'Tuner': 'Broadcast_Media',
            'USB': 'Media_USB',
            'VehicleControls': 'Vehicle_Controls',
            'VoiceRecognition': 'Voice',
            'WiFi': 'WiFi',
            'ZNonFunctional': 'Non_Functional'
        }
        return feature_group_mapping.get(original_name, original_name)

    def __get_all_test_cases(self):
        """Get all test cases from the robot files in the root directory."""
        try:
            robot_files = self.find_robot_files()
            all_test_cases = []
            for feature_group, files in robot_files.items():
                mapped_feature_group = ConvertRobotToExcel.map_feature_group_name(feature_group)
                for file_path in files:
                    if ConvertRobotToExcel.should_include_robot_file(os.path.basename(file_path)):
                        suite_name = os.path.splitext(os.path.basename(file_path))[0]
                        all_test_cases.extend(self.__parse_robot_file(file_path, suite_name, mapped_feature_group))
            return all_test_cases
        except Exception as exp:
            robot_print_error(f"Error to get all test cases, EXCEPTION: {exp}")

    def process_robot_files(self, test_sub_group, test_group, test_type):
        """Process all robot files and write extracted test cases to Excel.
        Args:
            test_sub_group (str): The subgroup to which the test cases belong.
            test_group (str): The group to which the test cases belong.
            test_type (str): The type of the test cases.
        """
        all_test_cases = self.__get_all_test_cases()
        self.__write_to_excel_new(all_test_cases, test_sub_group, test_group, test_type)

    def read_all_keys_from_excel(self):
        """Read all 'key' values from the Excel sheet 'Sheet1'.
        Reads the 'key' values from the Excel file located at the path obtained from `get_excel_file_path()`.
        Returns list: A list of 'key' values from the Excel sheet 'Sheet1'.
        """
        try:
            excel_file_path = str(self.get_excel_file_path)
            df = pd.read_excel(excel_file_path, sheet_name="Sheet1")
            keys = df['key'].tolist()
            keys = [key for key in keys if not (isinstance(key, float) and math.isnan(key))]
            return keys
        except Exception as exp:
            self.logger.error(f"Error reading keys from Excel: {exp}")
            return []

    def read_gherkin_data_from_excel(self, issue_key: str) -> str or None:
        """Read Gherkin data associated with a specific issue key from Excel.
        Args:
            issue_key (str): The issue key to find in the 'key' column of 'Sheet1' in the Excel file.
        Returns str or None: The formatted Gherkin data if found, otherwise None.
        """
        try:
            excel_file_path = str(self.get_excel_file_path)
            df = pd.read_excel(excel_file_path, sheet_name="Sheet1")
            row = df[df['key'] == issue_key].iloc[0]
            gherkin_data = row['gherkin_def']
            formatted_gherkin_data = gherkin_data.replace('\n', '\\n')
            return formatted_gherkin_data
        except Exception as exp:
            self.logger.error(f"Error reading Gherkin data from Excel: {exp}")
            return None

    def get_empty_key_with_summary_dataframe(self) -> pd.DataFrame or None:
        """Get DataFrame with test cases where 'key' is empty but 'summary' exists.
        Returns a DataFrame filtered from 'Sheet1' of the Excel file at `get_excel_file_path()`,
        containing rows where 'key' is empty or NaN but 'summary' exists.
        Returns pd.DataFrame or None: Filtered DataFrame with relevant columns if found, otherwise None.
        """
        try:
            excel_file_path = str(self.get_excel_file_path)
            df_all = pd.read_excel(excel_file_path, sheet_name="Sheet1")
            df_filtered = df_all[df_all['key'].isnull() | (df_all['key'] == '') & df_all['summary'].notna()]
            if 'Issue Links' not in df_all.columns:
                df_all['Issue Links'] = ''
            if not df_filtered.empty:
                df_filtered = df_filtered[
                    ['key', 'summary', 'gherkin_def', 'labels', 'Suite', 'Feature Group', 'Issue Links']].reset_index(drop=True)
                return df_filtered
            else:
                self.logger.error("No test cases found where 'key' is empty but 'summary' exists.")
                return None
        except Exception as exp:
            self.logger.error(f"Error to get empty key with summary, EXCEPTION: {exp}")

    def convert_to_json_format(self, test_sub_group, test_group, test_case_type):
        """Convert extracted test cases to the desired JSON format.
        Converts test cases from the Excel sheet 'Sheet1' into a JSON format suitable for further processing.
        This method retrieves relevant fields, sets up issue links, and formats Gherkin data accordingly.
        Args:
            test_sub_group (str): The subgroup to assign to each test case.
            test_group (str): The group to assign to each test case.
            test_case_type (str): The type of each test case.
        Returns str or None: Path to the JSON file if successful, otherwise None.
        """
        all_test_cases = self.get_empty_key_with_summary_dataframe()
        if all_test_cases is None:
            self.logger.info("No test cases found to convert.")
            return []

        json_data = []
        for idx, test_case in all_test_cases.iterrows():
            try:
                fields = self.get_required_fields_of_test_case(test_case.to_dict(), test_sub_group, test_group,
                                                               test_case_type)
                issuelinks = []
                if 'Issue Links' in test_case and isinstance(test_case['Issue Links'], str):
                    keys_from_documentation = [key.strip().strip("'") for key in
                                               test_case['Issue Links'].strip("[]").split(', ')]
                    for key in keys_from_documentation:
                        if key.strip():
                            issuelinks.append({
                                "add": {
                                    "type": {"name": "Test", "outward": "tests"},
                                    "outwardIssue": {"key": key.strip()}
                                }
                            })
                if issuelinks:
                    test_case_data = {
                        "testtype": "Cucumber",
                        "fields": fields,
                        "update": {
                            "issuelinks": issuelinks
                        },
                        "gherkin_def": test_case['gherkin_def']
                    }
                else:
                    test_case_data = {
                        "testtype": "Cucumber",
                        "fields": fields,
                        "gherkin_def": test_case['gherkin_def']
                    }
                json_data.append(test_case_data)
            except Exception as e:
                self.logger.error(f"Error processing test case at index {idx}: {e}")

        if not json_data:
            self.logger.error("No valid test cases converted.")
        formatted_json = json.dumps(json_data, indent=4)
        file_path = self.get_json_file_path()
        try:
            with open(file_path, 'w') as file:
                file.write(formatted_json)
            return file_path
        except Exception as e:
            self.logger.error(f"Error storing JSON data: {e}")
            return None

    def parse_robot_file_content(self, content):
        """Parse the content of a Robot Framework file into structured data.
        Args:
            content (str): The content of a Robot Framework file.
        Returns dict: Parsed sections including imports, setup/teardown, and test cases.
        """
        try:
            sections = {
                'imports': [],
                'Suite Setup': '',
                'Test Setup': '',
                'Test Teardown': '',
                'Suite Teardown': '',
                'test_cases': []
            }

            current_section = None
            current_test_case = None
            previous_line = ""

            for line in content.splitlines():
                stripped_line = line.strip()

                if stripped_line.startswith('*** Settings ***'):
                    current_section = 'settings'
                elif stripped_line.startswith('*** Test Cases ***'):
                    current_section = 'test_cases'
                elif stripped_line.startswith('Resource') or stripped_line.startswith(
                        'Variables') or stripped_line.startswith(
                    'Library'):
                    if current_section == 'settings':
                        sections['imports'].append(stripped_line)
                elif stripped_line.startswith('Suite Setup'):
                    sections['Suite Setup'] = stripped_line
                elif stripped_line.startswith('Test Setup'):
                    sections['Test Setup'] = stripped_line
                elif stripped_line.startswith('Test Teardown'):
                    sections['Test Teardown'] = stripped_line
                elif stripped_line.startswith('Suite Teardown'):
                    sections['Suite Teardown'] = stripped_line
                elif current_section == 'test_cases':
                    if not stripped_line:
                        current_test_case = None
                    elif current_test_case is None:
                        current_test_case = {'todo': '', 'name': '', 'tags': '', 'documentation': '', 'steps': []}
                        sections['test_cases'].append(current_test_case)
                        if stripped_line.startswith('#TODO'):
                            current_test_case['todo'] = stripped_line
                    elif stripped_line.startswith('[Tags]'):
                        current_test_case['tags'] = stripped_line
                        current_test_case['name'] = previous_line
                    elif stripped_line.startswith('[Documentation]'):
                        current_test_case['documentation'] = stripped_line
                    elif current_test_case['name'] != '':
                        current_test_case['steps'].append(stripped_line)
                previous_line = stripped_line
            return sections
        except Exception as exp:
            self.logger.error(f"Error to parse robot file content, EXCEPTION: {exp}")

    def collect_robot_files(self, summary_name, issue_key_value):
        """Collect Robot Framework files in a directory and parse their content.
        Args:
            summary_name (str): The name of the test case summary to find and update.
            issue_key_value (str): The issue key value to add in case of no file summary name and issue.
        Returns dict: Dictionary containing parsed content of Robot Framework files with updated file names.
        """
        try:
            robot_files = {}
            directory = os.path.join(self.common_keywords.get_root_path(), PROJECT, ROBOT_SCRIPTS, ROBOT_SCRIPTS_DIR_NAME)
            if not os.path.isdir(directory):
                directory = os.path.join(self.common_keywords.get_root_path(), PROJECT, TEAM_SWE5, TEST_CASES)
            for root, _, files in os.walk(directory):
                for file in files:
                    if self.should_include_robot_file(file):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        parsed_content = self.parse_robot_file_content(content)
                        robot_files[file] = parsed_content
                        for test_case in parsed_content['test_cases']:
                            summary = test_case['name']
                            if summary == summary_name:
                                prefixed_issue_key = f"TEST_{issue_key_value}"
                                if 'tags' not in test_case:
                                    test_case['tags'] = prefixed_issue_key
                                else:
                                    tags = test_case['tags'].strip().split()
                                    if prefixed_issue_key not in tags or issue_key_value not in tags:
                                        tags.append(prefixed_issue_key)
                                        test_case['tags'] = '  '.join(tags)
                                temp_file_name = os.path.splitext(file)[0] + '_temp.robot'
                                temp_file_path = os.path.join(root, temp_file_name)
                                with open(temp_file_path, 'w', encoding='utf-8') as temp_f:
                                    temp_f.write(self.generate_robot_file_content(parsed_content))
                                temp_f.close()
                                f.close()
                                os.remove(file_path)
                                os.rename(temp_file_path, file_path)
                                robot_files[file] = file_path
            return robot_files
        except Exception as exp:
            self.logger.error(f"Error to collect robot files, EXCEPTION: {exp}")

    def generate_robot_file_content(self, parsed_content):
        """Generate Robot file content from parsed sections.
        Args:
            parsed_content (dict): Parsed sections of a Robot Framework file.
        Returns str: Generated content of the Robot Framework file.
        """
        try:
            content_lines = ['*** Settings ***']
            for section_name, section_content in parsed_content.items():
                if section_name == 'imports':
                    for imp in section_content:
                        content_lines.append(imp)
                    content_lines.append('')
                elif section_name in ['Suite Setup', 'Test Setup', 'Test Teardown', 'Suite Teardown']:
                    if section_content:
                        content_lines.append(section_content)
                elif section_name == 'test_cases':
                    content_lines.append('')
                    content_lines.append('*** Test Cases ***')
                    for test_case in section_content:
                        if test_case['todo']:
                            content_lines.append(test_case['todo'])
                        content_lines.append(test_case['name'])
                        if test_case['tags']:
                            content_lines.append(f"    {test_case['tags']}")
                        if test_case['documentation']:
                            content_lines.append(f"    {test_case['documentation']}")
                        if test_case['steps']:
                            for step in test_case['steps']:
                                content_lines.append(f"    {step}")
                        content_lines.append('')
            return '\n'.join(line for line in content_lines)
        except Exception as exp:
            self.logger.error(f"Error to generate robot file content, EXCEPTION: {exp}")

    def create_test_case_dataframe(self):
        """Create a DataFrame with all test cases from Robot Framework files.
        Returns a DataFrame containing structured data extracted from Robot Framework files,
        including 'key', 'summary', 'gherkin_def', 'labels', 'Suite', 'Feature Group',
        'Test Group', 'Test Sub Group', and 'Test Case Type'.
        Returns pd.DataFrame or None: DataFrame with test case details if successful, otherwise None.
        """
        try:
            all_test_cases = self.__get_all_test_cases()

            if not all_test_cases:
                self.logger.info("No test cases found.")
                return None

            df_data = {
                'key': [],
                'summary': [],
                'gherkin_def': [],
                'labels': [],
                'Suite': [],
                'Feature Group': [],
                'Test Group': [],
                'Test Sub Group': [],
                'Test Case Type': []
            }

            for test_case in all_test_cases:
                df_data['key'].append(test_case['key'])
                df_data['summary'].append(test_case['summary'])
                df_data['gherkin_def'].append(test_case['gherkin_def'])
                df_data['labels'].append(test_case['labels'])
                df_data['Suite'].append(test_case['Suite'])
                df_data['Feature Group'].append(test_case['Feature Group'])
                df_data['Test Group'].append('')
                df_data['Test Sub Group'].append('')
                df_data['Test Case Type'].append('')

            df = pd.DataFrame(df_data)
            return df
        except Exception as exp:
            self.logger.error(f"Error to create test case df, EXCEPTION: {exp}")

    def read_all_issue_links_from_excel(self):
        """
        Read all issue links from the Excel sheet 'Sheet1'.
        Reads the 'key' and 'issue_links' values from the Excel file located at the path obtained from `get_excel_file_path()`.

        Returns:
            list: A list of tuples containing 'key' and 'issue_links' values from the Excel sheet 'Sheet1'.
        """
        try:
            excel_file_path = str(self.get_excel_file_path)
            df = pd.read_excel(excel_file_path, sheet_name="Sheet1")
            issue_links = []
            for key, links in zip(df['key'].dropna(), df['Issue Links'].dropna()):
                clean_key = key.replace("TEST_", "")
                issue_links.append((clean_key, links))
            return issue_links
        except Exception as exp:
            print(f"Error reading issue links from Excel: {exp}")
            return []
