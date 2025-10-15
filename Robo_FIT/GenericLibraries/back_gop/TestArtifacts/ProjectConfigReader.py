import json

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ProjectConfigReader:
    """
    This class encode the josn file and give the list, int, string values accordind to user need.
    """
    __config_list = None

    __instance = None

    @staticmethod
    def get_config_reader() -> 'ProjectConfigReader':
        if ProjectConfigReader.__instance is None:
            ProjectConfigReader()
        return ProjectConfigReader.__instance

    def __init__(self):
        if ProjectConfigReader.__instance is not None:
            raise Exception(
                f"{__class__} is a Singleton class, to create a object of this please use get_config_reader()")
        else:
            ProjectConfigReader.__instance = self
            # get path of the json file
            self.common_keywords = CommonKeywordsClass()
            # robot_print_debug(f"Config lIST: {ProjectConfigReader.__config_list}")
            if ProjectConfigReader.__config_list is None:
                ProjectConfigReader.__config_list = self.read_config_file(
                    self.common_keywords.get_project_config_path())

    def read_config_file(self, path):
        """
        This method read the config file
        :param path: path of the config file
        :return: after reading dile it returns Dictionary to the caller
        """
        with open(path) as json_file:
            try:

                dict = json.loads(json_file.read())
                return dict
            except ValueError as e:
                print("invalid json: %s" % e)
                return False

    def read_int(self, key):
        """
        This method convert the data into integer
        :param key: is the key in the json config file
        :return: return the integer value
        """
        try:
            return int(ProjectConfigReader.__config_list[key])
        except ValueError as e:
            print("invalid json value: %s" % e)

    def read_string(self, key):
        """
        This method convert the data into string
        :param key: is the key in the json config file
        :return: return the string value
        """
        try:
            return str(ProjectConfigReader.__config_list[key])
        except ValueError as e:
            print("invalid json value: %s" % e)

    def read_list(self, key):
        """
        This method read the list from the config file
        :param key: is the key in the json file
        :return: return the list or dictionary
        """
        try:
            return ProjectConfigReader.__config_list[key]
        except ValueError as e:
            print("invalid json value: %s" % e)
