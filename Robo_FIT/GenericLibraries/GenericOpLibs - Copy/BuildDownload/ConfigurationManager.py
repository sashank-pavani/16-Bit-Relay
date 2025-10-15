"""
ConfigurationManager class is used to manage and provide the JSON configuration information in
required format and validate that
"""


from Robo_FIT.GenericLibraries.GenericOpLibs.BuildDownload.ConfigurationReader import ConfigurationReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug


class ConfigurationManager:
    BUILD_VARIANT_KEY = "buildVariant"
    BUILD_URL_KEY = "buildUrl"
    BUILD_FOLDER_REGEX_KEY = "buildFolderRegex"
    BUILD_NAME_REGEX_KEY = "buildNameRegex"
    BUILD_EXT_REGEX_KEY = "buildExtension"

    def __init__(self):
        self.config = ConfigurationReader.get_configuration_reader()

    def get_jfrog_username(self) -> str:
        """
        This function will return the jfrog Username. It should be a CDSID of the user.
        :return: jfrog Username from JSON file
        :rtype: str
        """
        try:
            username = self.config.read_string("jfrogUsername")
            if username == "":
                raise WrongConfigurationValueProvided("jfrog user name can't be empty")
            return username
        except KeyError as err:
            robot_print_error(f"Error to get the jfrog username, EXCEPTION: {err}")

    def get_jfrog_password(self):
        """
        THis function is used to provide the jfrog password, User need to generate the
        jfrog password from the Jfrog.
        :return: Jfrog user generated password.
        :rtype: str
        """
        try:
            password = self.config.read_string("jfrogPassword")
            if password == "":
                raise WrongConfigurationValueProvided("jfrog password can't be empty")
            return password
        except KeyError as err:
            robot_print_error(f"Error to get the jfrog password, EXCEPTION: {err}")

    def get_build_variant_object(self, variant_name):
        """
        This function is used to get the build information from the JSON base the build variant.
        Information can be URL, Reg ex for build etc.
        :param variant_name: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_name: str
        :return: Dict format of the configuration.
        :rtype:
        """
        build_configs = self.config.read_list("buildConfigurations")
        if len(build_configs) == 0:
            raise WrongConfigurationValueProvided("Build configurations should be provided under "
                                                  "'buildConfigurations' key")
        for config in build_configs:
            if config[ConfigurationManager.BUILD_VARIANT_KEY] == variant_name:
                return config
        return None

    def get_jfrog_link_by_variant(self, variant_value):
        f"""
        This function is used to provide the Jfrog link base on the build variant value
        :param variant_value: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_value: str 
        :return: String value of the URL which user provided in #{ConfigurationManager.BUILD_URL_KEY}
        :rtype: str
        """
        try:
            variant_config = self.get_build_variant_object(variant_value)
            if variant_config is not None:
                return variant_config[ConfigurationManager.BUILD_URL_KEY]
        except WrongConfigurationValueProvided as exp:
            robot_print_error(f"Please provide the proper value in the configuration file, "
                              f"EXCEPTION: {exp}")

    def get_build_folder_regex_by_variant(self, variant_value):
        f"""
        This function is used to provide the build folder regex from the configuration.
        :param variant_value: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_value: str 
        :return: Build folder regex which user provided in JSON config key ${ConfigurationManager.BUILD_FOLDER_REGEX_KEY}
        :rtype: str
        """
        try:
            variant_config = self.get_build_variant_object(variant_value)
            if variant_config is not None:
                robot_print_debug(f"Folder regex: {variant_config[ConfigurationManager.BUILD_FOLDER_REGEX_KEY]}")
                return variant_config[ConfigurationManager.BUILD_FOLDER_REGEX_KEY]
        except WrongConfigurationValueProvided as exp:
            robot_print_error(f"Please provide the proper value in the configuration file, "
                              f"EXCEPTION: {exp}")

    def get_build_name_regex_by_variant(self, variant_value):
        f"""
        This function is used to provide the build name regex from the configuration.
        :param variant_value: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_value: str 
        :return: Build name regex which user provided in JSON config key ${ConfigurationManager.BUILD_NAME_REGEX_KEY}
        :rtype: str
        """
        try:
            variant_config = self.get_build_variant_object(variant_value)
            if variant_config is not None:
                robot_print_debug(f"Name regex: {variant_config[ConfigurationManager.BUILD_NAME_REGEX_KEY]}")
                return variant_config[ConfigurationManager.BUILD_NAME_REGEX_KEY]
        except WrongConfigurationValueProvided as exp:
            robot_print_error(f"Please provide the proper value in the configuration file, "
                              f"EXCEPTION: {exp}")

    def get_build_name_extension(self, variant_value):
        f"""
        This function is used to provide the build extension from the configuration.
        :param variant_value: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_value: str 
        :return: Build extension which user provided in JSON config key ${ConfigurationManager.BUILD_EXT_REGEX_KEY}
        :rtype: str 
        """
        try:
            variant_config = self.get_build_variant_object(variant_value)
            if variant_config is not None:
                return variant_config[ConfigurationManager.BUILD_EXT_REGEX_KEY]
        except WrongConfigurationValueProvided as exp:
            robot_print_error(f"Please provide the proper value in the configuration file, "
                              f"EXCEPTION: {exp}")


class WrongConfigurationValueProvided(Exception):
    """
    Custom exception created if any wrong value provided by the user in configuration file.
    """
    pass
