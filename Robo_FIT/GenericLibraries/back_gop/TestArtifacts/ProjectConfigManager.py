import json

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigReader import ProjectConfigReader


class ProjectConfigManager:
    """
    This class is used for the providing the different valued from the configuration file
    """

    def __init__(self):
        self.project_config_file = ProjectConfigReader.get_config_reader()

    def hardware_usb_adb_device_id(self):
        """
        This method read the W601 hardware ID from the configuration file
        :return: Hardware ID
        :exception if user not provide hardware id correctly the its throws JSONDecoderError
        """
        try:
            # "projectHardwareID and "deviceId" are the keys in the json file
            hardware_adb_id = self.project_config_file.read_list("projectHardwareId")
            return hardware_adb_id['deviceUsbId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def hardware_network_adb_device_id(self):
        """
        This method read the W601 hardware ID from the configuration file
        :return: Hardware ID
        :exception if user not provide hardware id correctly the its throws JSONDecoderError
        """
        try:
            # "projectHardwareID and "deviceId" are the keys in the json file
            hardware_info = self.project_config_file.read_list("projectHardwareId")
            return hardware_info['deviceNetworkId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def hardware_device_name(self):
        """
        This method read the W601 hardware name from the configuration file
        :return: Hardware name
        :exception if user not provide hardware name correctly the its throws JSONDecoderError
        """
        try:
            # "projectHardwareID and "deviceName" are the keys in the json file
            hardware_info = self.project_config_file.read_list("projectHardwareId")
            return hardware_info['deviceName'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_one_device_id(self):
        """
        This method read the First Bluetooth device id from the configuration file
        :return: First Bluetooth device id
        :exception if user not provide First Bluetooth device id correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneOne" and "deviceId" are the keys in the json file
            ext_phone_one_info = self.project_config_file.read_list("extPhoneOne")
            return ext_phone_one_info['deviceId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_one_device_name(self):
        """
        This method read the First Bluetooth device name from the configuration file
        :return: First Bluetooth device Name
        :exception if user not provide First Bluetooth device name correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneOne" and "deviceName" are the keys in the json file
            ext_phone_one_info = self.project_config_file.read_list("extPhoneOne")
            return ext_phone_one_info['deviceName'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_two_device_id(self):
        """
        This method read the Second Bluetooth device id from the configuration file
        :return: Second Bluetooth device id
        :exception if user not provide Second Bluetooth device id correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneTwo" and "deviceId" are the keys in the json file
            ext_phone_two_info = self.project_config_file.read_list("extPhoneTwo")
            return ext_phone_two_info['deviceId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_two_device_name(self):
        """
        This method read the Second Bluetooth device name from the configuration file
        :return: Second Bluetooth device name
        :exception if user not provide Second Bluetooth device name correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneTwo" and "deviceName" are the keys in the json file
            ext_phone_two_info = self.project_config_file.read_list("extPhoneTwo")
            return ext_phone_two_info['deviceName'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_three_device_id(self):
        """
        This method read the Third Bluetooth device id from the configuration file
        :return: Third Bluetooth device id
        :exception if user not provide Third Bluetooth device id correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneThree" and "deviceId" are the keys in the json file
            ext_phone_three_info = self.project_config_file.read_list("extPhoneThree")
            return ext_phone_three_info['deviceId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_three_device_name(self):
        """
        This method read the Third Bluetooth device name from the configuration file
        :return: Third Bluetooth device name
        :exception if user not provide Third Bluetooth device name correctly the its throws JSONDecoderError
        """
        try:
            # "extPhoneThree" and "deviceName" are the keys in the json file
            ext_phone_three_info = self.project_config_file.read_list("extPhoneThree")
            return ext_phone_three_info['deviceName'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_four_device_id(self):
        """
        This method read the Fourth Bluetooth device ID from the configuration file
        :return: Fourth Bluetooth device name
        :exception if user not provide Fourth Bluetooth device ID correctly the its throws JSONDecoderError
        """
        try:
            ext_phone_four_info = self.project_config_file.read_list("extPhoneFour")
            return ext_phone_four_info['deviceId'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def ext_phone_four_device_name(self):
        """
       This method read the Fourth Bluetooth device name from the configuration file
       :return: Fourth Bluetooth device name
       :exception if user not provide Fourth Bluetooth device name correctly the its throws JSONDecoderError
       """
        try:
            ext_phone_four_info = self.project_config_file.read_list("extPhoneFour")
            return ext_phone_four_info['deviceName'].strip()
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def get_project_name(self) -> str:
        """
        This function return Project Name
        :return: Project Name
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")
            return project_info['projectName']
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def get_project_enterproj_id(self) -> str:
        """
        This function returns Project enterProj ID
        :return: EnterProj ID
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")["enterProj"]
            return project_info
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")
            return ''

    def get_project_handler_class(self) -> str:
        """
        This function return Project Name
        :return: Project Name
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")
            return project_info['projectClassName']
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")
            return ''

    def project_build_info_command(self) -> str:
        """
        This function provide build info command
        :return: Build Info command of project
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")
            return project_info['buildInfoCommand']
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def get_boot_kpi_command(self) -> str:
        """
        This function provide project boot kpi command
        :return: Boot KPI Command
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")
            return project_info['bootKpiCommand']
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def get_team_name(self) -> str:
        """
        Provide the Team name
        :return: Team Name
        :rtype: String
        """
        try:
            project_info = self.project_config_file.read_list("projectInfo")
            return project_info['teamName']
        except Exception as exp:
            robot_print_error(f"Error to get the Team name from the configuration file, EXCEPTION: {exp}")

    def get_tag_list(self) -> list:
        """
        Provide Tag list given by user
        :return: Tag List
        :rtype: List
        """
        try:
            return self.project_config_file.read_list("tags")
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")

    def is_xray_upload_execution_record(self) -> bool:
        """
        Provide user action about uploading execution recoard or not.
        isImportExecutionRecord: true or isImportExecutionRecord: false
        :return: isImportExecutionRecord value form configuration
        :rtype: Bool
        """
        try:
            return bool(self.project_config_file.read_list("xrayImporter")["isImportExecutionRecord"])
        except Exception as exp:
            robot_print_error(f"Error to read the xrayImporter->isImportExecutionRecord key, EXCEPTION: {exp}")

    def xray_client_info(self) -> str:
        """
        Provide client info from configuration
        :return: Client Info
        :rtype: String
        """
        try:
            return json.dumps(self.project_config_file.read_list("xrayImporter")["clientInfo"])
        except Exception as exp:
            robot_print_error(f"Error to read the X-Ray client info, EXCEPTION: {exp}")

    def jira_user_email_id(self):
        return json.dumps(self.project_config_file.read_list("xrayImporter")["userJiraUser"]['emailId'])

    def jira_user_id(self):
        return json.dumps(self.project_config_file.read_list("xrayImporter")["userJiraUser"]['userId'])

    def jira_api_token(self):
        return json.dumps(self.project_config_file.read_list("xrayImporter")["userJiraUser"]['apiToken'])

    def jira_fields_needs_to_update(self):
        return json.dumps(self.project_config_file.read_list("xrayImporter")["userJiraUser"]['updateFields'])

    def jira_get_component_name(self) -> str:
        return self.project_config_file.read_list("xrayImporter")["jiraComponentName"]

    def get_certificate_path(self) -> str:
        """
        Provide the certificate path give by user in Configuation
        :return: Certificate Path, value of zscalerCertificatePath
        :rtype: path
        """
        return self.project_config_file.read_list("xrayImporter")["zscalerCertificatePath"]

    def get_project_test_execution_key(self) -> str:
        """
        Provide Jira project Key
        :return: Project Key
        :rtype: String
        """
        return self.project_config_file.read_list("xrayImporter")["projectJiraKeys"]["projectTestExecutionKey"]

    def get_project_test_case_key(self):
        return self.project_config_file.read_list("xrayImporter")["projectJiraKeys"]["projectTestCaseKey"]

    def get_xray_environment(self):
        """
        Provide Environment of XRAY. Value can be "jenkins", "local"
        :return: xrayImporter -> environment value
        :rtype: str
        """
        return self.project_config_file.read_list("xrayImporter")["environment"]

    def get_jenkins_user_name(self):
        return self.project_config_file.read_list("jenkinsConfigurations")["username"]

    def get_jenkins_user_password(self):
        return self.project_config_file.read_list("jenkinsConfigurations")["password"]

    def get_jenkins_baseline_url(self):
        return self.project_config_file.read_list("jenkinsConfigurations")["buildBaselineUrl"]

    def jira_server_domain_url(self):
        return json.dumps(self.project_config_file.read_list("xrayImporter")["userJiraUser"]['serverDomain'])

    def get_grafana_base_url(self) -> str:
        """
        This function returns grafana dashboard base URL
        :return: Base URL
        :rtype: String
        """
        try:
            base_url = self.project_config_file.read_list("grafanaDashboardInfo")["baseUrl"]
            if base_url.endswith('/'):
                base_url = base_url[:-1]
            return base_url
        except json.JSONDecodeError as exp:
            robot_print_error(f"EXCEPTION:{exp}")
            return ''

    def is_upload_record_to_grafana(self) -> bool:
        """
        Provide user action about uploading record on Grafana dashboard or not.
        isUploadRecordOnGrafana: true or isUploadRecordOnGrafana: false
        :return: isUploadRecordOnGrafana value form configuration
        :rtype: Bool
        """
        try:
            return bool(self.project_config_file.read_list("grafanaDashboardInfo")["isUploadRecordOnGrafana"])
        except Exception as exp:
            robot_print_error(f"Error to read the xrayImporter->isImportExecutionRecord key, EXCEPTION: {exp}")

    def get_the_list_of_packages(self) -> list:
        """
        Provide user action about getting the package list from the config file.
        it is used to return the list of packages from the config file
        :return: list of packages from the service file
        :rtype: list
        """
        try:
            grafana_info = self.project_config_file.read_list("grafanaDashboardInfo")["packageNames"]
            return grafana_info
        except KeyError as exp:
            robot_print_error(f"Error:'packageNames' key not found in the configuration file, EXCEPTION: {exp} ")

    # Function is for BDD handling the External Device,
    # For BDD project_config_file.json file is updated, and a new key value pair is introduced
    def get_ext_device_name(self, ext_device_type):
        try:
            return self.project_config_file.read_list("externalDevicesInfo")[ext_device_type]["deviceName"]
        except KeyError as exp:
            robot_print_warning(f"Given: {ext_device_type} is not available in configuration file. "
                                f"Please ignore if you are not using BDD structure, {exp}")

    def get_ext_device_id(self, ext_device_type):
        try:
            return self.project_config_file.read_list("externalDevicesInfo")[ext_device_type]["deviceId"]
        except KeyError as exp:
            robot_print_warning(f"Given: {ext_device_type} is not available in configuration file. "
                                f"Please ignore if you are not using BDD structure, {exp}")
            return None
