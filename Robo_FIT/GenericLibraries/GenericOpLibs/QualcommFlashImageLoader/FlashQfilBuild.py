import os
import subprocess
import sys
import shutil
from tarfile import is_tarfile
import zipfile
from time import sleep

from Robo_FIT.GenericLibraries.GenericOpLibs.QualcommFlashImageLoader.QfilAutomation import QfilAutomation
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class FlashQfilBuild:
    """
    This class is used to define different flashing procedures like Meta Build, provisioning etc.
    """

    def __init__(self):
        self.command_keywords = CommonKeywordsClass()

    def __print_error_line(self):
        """
        Used to print the more info related to exception
        :return: None
        :rtype: None
        """
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}", print_in_report=True)

    def delete_build_from_dir(self, action: str = "all"):
        """
        Used to delete the old build from the Build Dir
        :param action: if action is "all" means delete everything from the Build directory.
                        action is "ext" means delete only extract build directories.
        :type action: String
        :return: None
        :rtype: None
        """
        try:
            path = os.path.join(self.command_keywords.get_root_path(), PROJECT, CRE_LIBRARIES,
                                CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_INPUT_BUILD_DIR)
            for files in os.listdir(path):
                if action == "ext":
                    if os.path.isdir(os.path.join(path, files)):
                        robot_print_debug(f"Remove directory: {os.path.join(path, files)}")
                        comamnd = f"rmdir /Q /s {os.path.join(path, files)}"
                        robot_print_debug(f"Remove command: {comamnd}")
                        subprocess.run(comamnd, shell=True, stdout=subprocess.PIPE)
                        robot_print_info(f"File {files} remove successfully")
                if action == "all":
                    compress_file_path = os.path.join(path, files)
                    if compress_file_path.endswith("zip") or compress_file_path.endswith(".7z") \
                            or compress_file_path.endswith(".tar") or compress_file_path.endswith(".tar.gz"):
                        robot_print_debug(f"Compressed file deleting: {compress_file_path}")
                        os.remove(compress_file_path)
                    else:
                        robot_print_debug(f"Removing : {os.path.join(path, files)}")
                        comamnd = f"rmdir /Q /s {os.path.join(path, files)}"
                        robot_print_debug(f"Remove command: {comamnd}")
                        subprocess.run(comamnd, shell=True, stdout=subprocess.PIPE)
                        robot_print_info(f"File {files} remove successfully")
        except Exception as exp:
            robot_print_error(f"Error to delete the build, EXCEPTION: {exp}", print_in_report=True)
            self.__print_error_line()

    def extract_build(self, build_name: str = None) -> bool:
        """
        this method is used to extract the given build. Build should be in Build directory
        :param build_name: Name of build which need to be extract
        :type build_name: String
        :return: True if extract successfully, otherwise False
        :rtype: bool
        """
        build_dir = None
        try:
            build_dir = os.path.join(self.command_keywords.get_root_path(), PROJECT,
                                     CRE_LIBRARIES, CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_INPUT_BUILD_DIR)
            if os.path.isdir(build_dir):
                build_path = None
                if build_name is not None:
                    build_path = os.path.join(build_dir, build_name)
                    if is_tarfile(build_path) or build_path.endswith(".zip"):
                        robot_print_info(f"Build file path is : {build_path}")
                    else:
                        robot_print_error(f"It seems not tar or zip file in the {build_dir} dir",
                                          print_in_report=True)
                        return False
                else:
                    # build_name not provided
                    # means only one build is inside Build Dir
                    for build in os.listdir(build_dir):
                        build_path = os.path.join(build_dir, build)
                        if is_tarfile(build_path) or build_path.endswith(".zip"):
                            robot_print_info(f"Build file path is : {build_path}")
                        else:
                            robot_print_error(f"It seems {build_path} not a zip file",
                                              print_in_report=True)
                if build_path is not None:
                    try:
                        robot_print_info(f"Build Path: {build_dir}, build : {build_path}")
                        extract_cmd = "tar -v --extract --file {source} -C {destination}".format(
                            source=build_path, destination=build_dir)
                        robot_print_info(f"Extract Command: {extract_cmd}")
                        extract_cmd_out = subprocess.Popen(extract_cmd, shell=True, stdin=subprocess.PIPE,
                                                           stdout=subprocess.PIPE)
                        out, err = extract_cmd_out.communicate()
                        if not err:
                            if out.decode("utf-8") == "":
                                robot_print_info(f"Success Extract")
                                return True
                            else:
                                robot_print_error(f"Not Success")
                        else:
                            robot_print_error("Not success and there is and error %s" % err)
                    except zipfile.BadZipFile as err:
                        robot_print_error(f"Error to extract the file, EXCEPTION: {err}",
                                          print_in_report=True)
                else:
                    robot_print_error(f"No build found", print_in_report=True)
                    raise FileNotFoundError("No build file found")
            else:
                robot_print_error(f"It seems build directory not found", print_in_report=True)
                raise NotADirectoryError(f"{build_dir} is not a directory")
        except Exception as exp:
            robot_print_error(f"Error to extract the build form location: {build_dir}, EXCEPTION: {exp}",
                              print_in_report=True)
            self.__print_error_line()

    def flash_meta_build(self, flavours: str, flashing_time: int = 300, delete_type: str= "ext") -> bool:
        """
        This method is used to flash the Meta Build
        :param: flavours: Product Flavour
        :type: flavours: String
        :param: flashing_time: max time which is taken to flash the board. Should be in seconds
            Default is 300 seconds(5 minutes)
        :type: flashing_time: Int
        :param: delete_type: if user pass "ext" means user only want to delete the extract build
            if user pass "all" means user want to delete every thing from "CRE/Libraries/ExternalFiles/InputFiles/Build"
            path
        :type: delete_type: String, Default is "ext"
        :return: True if flashing success otherwise False
        :rtype: bool
        """
        qfil = None
        is_success = False
        try:
            self.delete_build_from_dir(action=delete_type)
            if self.extract_build():
                qfil = QfilAutomation()
                if qfil.check_port():
                    qfil.meta_build()
                    # load contents.xml file
                    qfil.load_content()
                    # product flavour select
                    qfil.select_product_flavors(flavors=flavours)
                    # load elf file
                    qfil.browse_programmer_path()
                    # click on download
                    if qfil.download_content():
                        sleep(flashing_time)
                        path = qfil.get_status()
                        sleep(10)
                        if path is not None:
                            with open(path, "r") as fp:
                                line = fp.readline()
                                while line:
                                    if "Download Succeed" in line:
                                        robot_print_info(f"Build Flash successfully")
                                        is_success = True
                                    line = fp.readline()
                        else:
                            robot_print_error(f"None path for read logs")
                            is_success = False
                        if is_success:
                            robot_print_info(f"Build flash successfully")
                            qfil.exit_qfil()
                        else:
                            robot_print_error(f"It seems error to download the build, Please check manually")
                            qfil.exit_qfil()
                else:
                    qfil.exit_qfil()
            return is_success
        except Exception as exp:
            robot_print_error(f"Error to flash the meta build, EXCEPTION: {exp}")
            if qfil is not None:
                qfil.capture_qfil_screenshot("ErrorMetaBuild")
            self.__print_error_line()
            return False

    def provisioning_board(self, flashing_time: int = 180, delete_type: str = "ext") -> bool:
        """
        This method is used to flash the provisioning build.
        :param: flashing_time: max time which is taken to flash the board. Should be in seconds
            Default is 180 seconds(3 minutes)
        :type: flashing_time: Int
        :param: delete_type: if user pass "ext" means user only want to delete the extract build
            if user pass "all" means user want to delete every thing from "CRE/Libraries/ExternalFiles/InputFiles/Build"
            path
        :type: delete_type: String, Default is "ext"
        :return: True if flashing success otherwise False
        :rtype: bool
        """
        qfil = None
        is_success = False
        try:
            self.delete_build_from_dir(action=delete_type)
            if self.extract_build():
                qfil = QfilAutomation()
                if qfil.check_port():
                    if qfil.provision_select_from_configuration():
                        qfil.provision_browser_xml()
                        qfil.browse_programmer_path()
                        if qfil.click_provision_button():
                            sleep(flashing_time)
                            path = qfil.get_status()
                            sleep(10)
                            if path is not None:
                                with open(path, "r") as fp:
                                    line = fp.readline()
                                    while line:
                                        if "Download Succeed" in line:
                                            robot_print_info(f"Build Flash successfully")
                                            is_success = True
                                        line = fp.readline()
                        else:
                            qfil.exit_qfil()
            return is_success
        except Exception as exp:
            robot_print_error(f"Error to provisioning the board, EXCEPTION: {exp}", print_in_report=True)
            self.__print_error_line()
            if qfil is not None:
                qfil.capture_qfil_screenshot("ErrorProvision")
            return False

