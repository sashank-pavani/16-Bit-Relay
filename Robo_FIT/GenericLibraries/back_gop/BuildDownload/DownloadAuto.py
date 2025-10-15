import os
import sys
from datetime import datetime
import re
import subprocess
from typing import Union

import requests
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, CRE_LIBRARIES, CRE_EXTERNAL_FILES, \
    CRE_INPUT_FILES, TEST_REPORTS, CRE_BUILD_INFO_FILE
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug, \
    robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.BuildDownload.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.BuildDownload.ConfigurationManager import WrongConfigurationValueProvided
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from bs4 import BeautifulSoup


class DownloadAuto:

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()
        self.config_manager = ConfigurationManager()
        self.user_name = self.config_manager.get_jfrog_username()
        self.user_password = self.config_manager.get_jfrog_password()

    def __get_build_folder(self):
        """
        This method will check if the build folder exists or not. If not, then
        create the Build folder in CRE/Libraries/ExternalFiles/InputFiles.
        """
        if "Build" not in os.listdir(os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                                  CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES)):
            os.mkdir(os.path.join(self.common_keyword.get_root_path(), PROJECT,
                                  CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES, "Build"), mode=0o777)
            robot_print_debug(f"Created Build folder")
        return os.path.join(self.common_keyword.get_root_path(), PROJECT,
                            CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES, "Build")

    def __get_build_url(self, jfrog_url: str):
        """
        This function will construct build download url base on the jforg_url

        URL format: http://<username>:<password>@<jfrog_url>
        :param jfrog_url: Jfrog URL which is used to download the build
        :type jfrog_url: str
        :return: Jfrog build URL with username and password
        :rtype: str
        """
        robot_print_debug(f"URL is: https://{self.user_name}:{self.user_password}@{jfrog_url}")
        return f"https://{self.user_name}:{self.user_password}@{jfrog_url}"

    def get_page_content(self, jfrog_url) -> str:
        """
        This function will get the HTML page content and return. It will send a request to given jfrog_url and
        return the content
        :param jfrog_url: Jfrog URL which is used to download the build
        :type jfrog_url: str
        :return: Content of the HTML page into string format
        :rtype: str
        """
        try:
            response = requests.get(self.__get_build_url(jfrog_url=jfrog_url), verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html5lib")
                return str(soup.contents[1])
            raise BadRequest(f"Bad request, status code: {response.status_code}, url: "
                             f"{self.__get_build_url(jfrog_url=jfrog_url)}")
        except Exception as exp:
            robot_print_error(f"Error to get the content of {jfrog_url}, EXCEPTION: {exp}")

    def __get_build_found_date(self, pick_for_date):
        """
        This function is used to check the build date and it will convert that into datetime object.
        :param pick_for_date: Date of the build which user wants to download.

        pick_for_date can be:
            1. "latest": Which means user wants to download the latest build from the JFROG
            2. "DD-MMM-YYYY": If a user provides in this format, then it will convert the value into a datetime object
                and download that build. For example, "19-Oct-2023".
        :type pick_for_date: str
        :return:  if pick_for_date == latest then it will return current datetime as a datetime object
                  else: it will convert the user given date into a datetime object.
        :rtype:
        """
        if pick_for_date == "latest":
            return datetime.now().date()
        return datetime.strptime(pick_for_date, "%d-%b-%Y").date()

    def __trigger_download_build_command(self, url):
        """
        THis function will trigger the build download command download the build for given URL.
        Build will be stored under '<homepath>/CRE/Libraries/ExternalFiles/InputFiles/Build
        :param url: URL from user wants to download the build
        :type url: str
        :return: None
        :rtype: None
        """
        robot_print_debug(f"Build folder: {self.__get_build_folder()}")
        process = subprocess.Popen(f"cd {self.__get_build_folder()} && "
                                   f"curl -u {self.user_name}:{self.user_password} -O {url}",
                                   shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        out, error = process.communicate()
        robot_print_info(f"Output: {out}\n\n\nError: {error}")

    def __get_build_from_link(self, jfrog_url, regex_value, pick_for_date="latest") -> Union[str, None]:
        """
        This function get the build form the give link and look fpr regex value.
        :param jfrog_url: Jfrog URL where user wants to download the build.
        :type jfrog_url: str
        :param regex_value: Regular expression to find the build.
        :type regex_value: str
         :param pick_for_date: Date of the build which user wants to download.

        pick_for_date can be:
            1. "latest": Which means user wants to download the latest build from the JFROG
            2. "DD-MMM-YYYY": If a user provides in this format, then it will convert the value into a datetime object
                and download that build. For example, "19-Oct-2023".
        :type pick_for_date: str
        :return: Name of the build which it is found base on regex, if no buidl found return None
        :rtype: str | None
        """
        try:
            contents = self.get_page_content(jfrog_url=jfrog_url).split("\n")
            found_build_for_date = self.__get_build_found_date(pick_for_date=pick_for_date)
            robot_print_info(f"Looking build for date = {found_build_for_date}")
            for index, html_data in enumerate(contents):
                if "</a>" in html_data:
                    data = re.findall("\d{2}-\w{3}-\d{4}", html_data)
                    if len(data) == 1:
                        date_found = datetime.strptime(data[0], "%d-%b-%Y").date()
                        if date_found == found_build_for_date:
                            build_name = re.findall(re.compile(regex_value), html_data)
                            if len(build_name) >= 1:
                                robot_print_debug(f"Build found as : {build_name[-1]}")
                                return build_name[-1]
        except Exception as exp:
            robot_print_error(f"Error to get the build from link: {jfrog_url}, EXCEPTION: {exp}")

    def download_build(self, variant_value, pick_for_date="latest"):
        """
        This is the main function will maintain the flow of downloading the build.
        :param variant_name: Name of the build variant, which user provided
            in the Configuration file as 'buildVariant' KEY
        :type variant_name: str
        :param pick_for_date: Date of the build which user wants to download.

        pick_for_date can be:
            1. "latest": Which means user wants to download the latest build from the JFROG
            2. "DD-MMM-YYYY": If a user provides in this format, then it will convert the value into a datetime object
                and download that build. For example, "19-Oct-2023".
        :type pick_for_date: str
        :return: None
        :rtype: None
        """
        jfrog_url = self.config_manager.get_jfrog_link_by_variant(variant_value)
        try:
            build_name, build_folder_name = None, None
            build_folder_name = self.__get_build_from_link(jfrog_url,
                                                           self.config_manager.get_build_folder_regex_by_variant(
                                                               variant_value),
                                                           pick_for_date=pick_for_date)
            if build_folder_name is not None:
                build_name = self.__get_build_from_link(f"{jfrog_url}/{build_folder_name}",
                                                        self.config_manager.get_build_name_regex_by_variant(
                                                            variant_value),
                                                        pick_for_date=pick_for_date)
            if build_name is not None and build_folder_name is not None:
                build_ext = self.config_manager.get_build_name_extension(variant_value)
                if f"{build_name}{build_ext}" not in os.listdir(self.__get_build_folder()):
                    # write the build name in BuildInfo.txt file
                    self.write_build_name_in_file(build_name=build_name)
                    # create build download URL and execute crul command to download it.
                    build_download_url = f"{self.__get_build_url(jfrog_url)}/{build_folder_name}/{build_name}{build_ext}"
                    robot_print_info(f"Starting download build from url: {build_download_url}")
                    self.__trigger_download_build_command(build_download_url)
            else:
                raise BuildNotFoundException(
                    f"No build found for given date: {self.__get_build_found_date(pick_for_date)}")
        except Exception as exp:
            robot_print_error(f"Error to download the build form url: {jfrog_url}, EXCEPTION: {exp}")
            sys.exit(-1)

    def write_build_name_in_file(self, build_name):
        file_path = os.path.join(self.common_keyword.get_root_path(), PROJECT, CRE_LIBRARIES,
                                 CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_BUILD_INFO_FILE)
        try:
            with open(file_path, "w") as fp:
                fp.write(build_name)
                fp.close()
        except IOError as err:
            robot_print_error(f"Error to write the build name: {build_name} in file: {file_path}, EXCEPTION: {err}")
            raise IOError(err)


class BuildNotFoundException(Exception):
    """Custom exception if Build no found."""
    pass


class BadRequest(Exception):
    """If there is a bad request send to the server, function will raise this exception. It's an custom exception"""
    pass
