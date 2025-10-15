from Robo_FIT.GenericLibraries.GenericOpLibs.QualcommFlashImageLoader.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class ConfiguratorManager:
    """
    THis class handle the QFIL config file.
    """

    def __init__(self):
        self.config_reader = ConfigurationReader()

    def get_qfil_exe_file_path(self) -> str:
        """
        This method is used to get the QFIL exe file path
        :return: It return QFIL exe file which is mention in config file with key 'qfilExePath'
        """
        try:
            return self.config_reader.read_string("qfilExePath")
        except Exception as exp:
            robot_print_error(f"Error to get the Qfil EXE file path, Please mention that in config file with"
                              f" key 'qfilExePath', EXCEPTION: {exp}")

    def get_qfil_log_path(self) -> str:
        """
        This method is used to get the Qfil Logs file Name which is mention in config file as
        'qfilLogsFileName' name.
        :return: Log file Name
        :rtype: String
        """
        try:
            return self.config_reader.read_string("qfilLogsFileName")
        except Exception as exp:
            robot_print_error(f"Error to get the Qfil Log file name, Please mention that in config file with"
                              f" key 'qfilLogsFileName', EXCEPTION: {exp}")

    def get_qfil_browser_file_path(self) -> str:
        """
        This method is used to get the Qfil .elf file path which is mention in config file as
        'browseFilePath' name.
        :return: .elf file path
        :rtype: String
        """
        try:
            return self.config_reader.read_string("browseFilePath")
        except Exception as exp:
            robot_print_error(f"Error to get the Qfil Browser file Path, Please mention that in config file with"
                              f" key 'browseFilePath', EXCEPTION: {exp}")

    def get_qfil_load_content_file_path(self) -> str:
        """
        This method is used to get the Qfil content.xml file name which is mention in config file as
        'loadContentPath' name.
        :return: content.xml file path
        :rtype: String
        """
        try:
            return self.config_reader.read_string("loadContentPath")
        except Exception as exp:
            robot_print_error(f"Error to get the Qfil contents.xml file Path, Please mention that in config file with"
                              f" key 'loadContentPath', EXCEPTION: {exp}")

    def get_provision_xml_path(self) -> str:
        """
        This method is used to get the Qfil provision .xml file name which is mention in config file as
        'provisionXmlPath' name.
        :return: provision .xml file path
        :rtype: String
        """
        try:
            return self.config_reader.read_string("provisionXmlPath")
        except Exception as exp:
            robot_print_error(f"Error to get the Qfil provision contents.xml file Path,"
                              f" Please mention that in config file with"
                              f" key 'provisionXmlPath', EXCEPTION: {exp}")
