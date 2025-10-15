import re
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import PROJECT, CRE_LIBRARIES, \
    CRE_EXTERNAL_FILES, CRE_DB_FILES, CRE_INPUT_FILES, ROBO_CAN_INPUT_FILE_NAME
from Robo_FIT.GenericLibraries.GenericOpLibs.AutoDL.ConfiguratorReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass


class ConfigurationManager:
    """
    This class is for CAN->to manage configuration 
    """

    def __init__(self):
        self.common_keyword = CommonKeywordsClass()
        self.config_reader = ConfiguratorReader()


    def get_job_name(self):
        try:
            return self.config_reader.read_list("job_name")

        except TypeError:
            robot_print_error("'job_name' not present in autoflash_config_file.json")

    def get_jenkins_server(self):
        try:
            return self.config_reader.read_list("jenkins_server")

        except TypeError:
            robot_print_error("'jenkins_server' not present in autoflash_config_file.json")

    def get_jenkins_user(self):
        try:
            return self.config_reader.read_list("jenkins_user")

        except TypeError:
            robot_print_error("'jenkins_user' not present in autoflash_config_file.json")

    def get_jenkins_token(self):
        try:
            return self.config_reader.read_list("jenkins_token")

        except TypeError:
            robot_print_error("'jenkins_token' not present in autoflash_config_file.json")

    def get_pending_stage(self):
        try:
            return self.config_reader.read_list("pending_stage")

        except TypeError:
            robot_print_error("'pending_stage' not present in autoflash_config_file.json")

    def get_ssh_host(self):
        try:
            return self.config_reader.read_list("ssh_host")

        except TypeError:
            robot_print_error("'ssh_host' not present in autoflash_config_file.json")

    def get_ssh_username(self):
        try:
            return self.config_reader.read_list("ssh_linux_username")

        except TypeError:
            robot_print_error("'ssh_linux_username' not present in autoflash_config_file.json")

    def get_ssh_password(self):
        try:
            return self.config_reader.read_list("ssh_linux_password")

        except TypeError:
            robot_print_error("'ssh_linux_password' not present in autoflash_config_file.json")

    def get_server_folder(self):
        try:
            return self.config_reader.read_list("server_USB_PKG_folder")

        except TypeError:
            robot_print_error("'server_USB_PKG_folder' not present in autoflash_config_file.json")

    def get_local_destination(self):
        try:
            return self.config_reader.read_list("USB_PKG_destination")

        except TypeError:
            robot_print_error("'USB_PKG_destination' not present in autoflash_config_file.json")

    def get_Mounted_Drive(self):
        try:
            return self.config_reader.read_list("Mounted_Drive")

        except TypeError:
            robot_print_error("'Mounted_Drive' not present in autoflash_config_file.json")

    def get_uuu_toolpath(self):
        try:
            return self.config_reader.read_list("UUU_Tool_Path")

        except TypeError:
            robot_print_error("'UUU_Tool_Path' not present in autoflash_config_file.json")

    def get_nfs_shared_folder(self):
        try:
            return self.config_reader.read_list("nfs_shared_folder")

        except TypeError:
            robot_print_error("'nfs_shared_folder' not present in autoflash_config_file.json")

    def get_reportpath(self):
        try:
            return self.config_reader.read_list("reportpath")

        except TypeError:
            robot_print_error("'reportpath' not present in autoflash_config_file.json")
            
    def get_jenkins_workspace(self):
        try:
            return self.config_reader.read_list("jenkins_workspace")

        except TypeError:
            robot_print_error("'jenkins_workspace' not present in autoflash_config_file.json")
            
            

