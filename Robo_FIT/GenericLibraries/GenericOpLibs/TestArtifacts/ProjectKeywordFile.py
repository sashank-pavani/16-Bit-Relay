from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager
from Robo_FIT.GenericLibraries.GenericOpLibs.AppiumSession.StartAppiumSession import StartAppiumSession
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
import os


class ProjectKeywordFile:

    def __init__(self):
        try:
            # TODO: Is need to provide the path of prject_config_file.json in this file?
            self.common_keywords = CommonKeywordsClass()
            # robot_print_debug(f"Keyword file: {}")
            self.project_config_manager = ProjectConfigManager()
            try:
                self.start_appium_session = StartAppiumSession()
            except Exception as exp:
                robot_print_debug(f"it seems user doesn't wants to use the Appium, EXCEPTION: {exp}")
                self.start_appium_session = None
            file_path = os.path.join(self.common_keywords.get_project_keywords_dir_path(),  "project_keyword.py")
            with open(file_path, "w") as project_file:
                project_file.write("PROJECT_HARDWARE_DEVICE_ID = \"{hardwaredeviceid}\"\n".format(
                    hardwaredeviceid=self.project_config_manager.hardware_network_adb_device_id()))
                project_file.write("PROJECT_HARDWARE_USB_DEVICE_ID = \"{hardwaredeviceid}\"\n".format(
                    hardwaredeviceid=self.project_config_manager.hardware_usb_adb_device_id()))
                project_file.write("PROJECT_HARDWARE_DEVICE_NAME = \"{hardwaredevicename}\"\n".format(
                    hardwaredevicename=self.project_config_manager.hardware_device_name()))
                self.__write_ext_device_id_name(project_file)
                if self.start_appium_session is not None:
                    project_file.write("HARDWARE_URL = \"{hardwareurl}\"\n".format(
                        hardwareurl=self.start_appium_session.hardware_appium_url()))
                    project_file.write("EXT_PHONE_ONE_URL = \"{extphoneoneurl}\"\n".format(
                        extphoneoneurl=self.start_appium_session.ext_phone_one_appium_url()))
                    project_file.write("EXT_PHONE_TWO_URL = \"{extphonetwourl}\"\n".format(
                        extphonetwourl=self.start_appium_session.ext_phone_two_appium_url()))
                    project_file.write("EXT_PHONE_THREE_URL = \"{extphonethreeurl}\"\n".format(
                        extphonethreeurl=self.start_appium_session.ext_phone_three_appium_url()))
                    project_file.write("EXT_PHONE_FOUR_URL = \"{extphonefoururl}\"\n".format(
                        extphonefoururl=self.start_appium_session.ext_phone_four_appium_url()))
                project_file.write("BOOT_KPI_CMD  = \"{bootkpicmd}\"\n".format(
                    bootkpicmd=self.project_config_manager.get_boot_kpi_command()))
                project_file.close()
        except IOError as excep:
            print(excep)

    def __write_ext_device_id_name(self, project_file):
        try:
            if self.project_config_manager.get_ext_device_name(FAREND_DEVICE_TYPE_BT_CONN_1) is None:
                project_file.write("EXT_PHONE_ONE_DEVICE_ID = \"{extonedeviceid}\"\n".format(
                    extonedeviceid=self.project_config_manager.ext_phone_one_device_id()))
                project_file.write("EXT_PHONE_ONE_DEVICE_NAME = \"{extonedevicename}\"\n".format(
                    extonedevicename=self.project_config_manager.ext_phone_one_device_name()))
                project_file.write("EXT_PHONE_TWO_DEVICE_ID = \"{exttwodeviceid}\"\n".format(
                    exttwodeviceid=self.project_config_manager.ext_phone_two_device_id()))
                project_file.write("EXT_PHONE_TWO_DEVICE_NAME = \"{exttwodevicename}\"\n".format(
                    exttwodevicename=self.project_config_manager.ext_phone_two_device_name()))
                project_file.write("EXT_PHONE_THREE_DEVICE_ID = \"{extthreedeviceid}\"\n".format(
                    extthreedeviceid=self.project_config_manager.ext_phone_three_device_id()))
                project_file.write("EXT_PHONE_THREE_DEVICE_NAME = \"{extthreedevicename}\"\n".format(
                    extthreedevicename=self.project_config_manager.ext_phone_three_device_name()))
                project_file.write("EXT_PHONE_FOUR_DEVICE_ID = \"{extfourdeviceid}\"\n".format(
                    extfourdeviceid=self.project_config_manager.ext_phone_four_device_id()))
                project_file.write("EXT_PHONE_FOUR_DEVICE_NAME = \"{extfourdevicename}\"\n".format(
                    extfourdevicename=self.project_config_manager.ext_phone_four_device_name()))
            else:
                project_file.write("BT_CONNECTION_ONE_ID = \"{extonedeviceid}\"\n".format(
                    extonedeviceid=self.project_config_manager.get_ext_device_id(FAREND_DEVICE_TYPE_BT_CONN_1)))
                project_file.write("BT_CONNECTION_ONE_NAME = \"{extonedevicename}\"\n".format(
                    extonedevicename=self.project_config_manager.get_ext_device_name(FAREND_DEVICE_TYPE_BT_CONN_1)))
                project_file.write("BT_CONNECTION_TWO_ID = \"{exttwodeviceid}\"\n".format(
                    exttwodeviceid=self.project_config_manager.get_ext_device_id(FAREND_DEVICE_TYPE_BT_CONN_2)))
                project_file.write("BT_CONNECTION_TWO_NAME = \"{exttwodevicename}\"\n".format(
                    exttwodevicename=self.project_config_manager.get_ext_device_name(FAREND_DEVICE_TYPE_BT_CONN_2)))
                project_file.write("CALLING_DEVICE_ONE_ID = \"{extthreedeviceid}\"\n".format(
                    extthreedeviceid=self.project_config_manager.get_ext_device_id(FAREND_DEVICE_TYPE_CALLING_ONLY_1)))
                project_file.write("CALLING_DEVICE_ONE_NAME = \"{extthreedevicename}\"\n".format(
                    extthreedevicename=self.project_config_manager.get_ext_device_name(FAREND_DEVICE_TYPE_CALLING_ONLY_1)))
                project_file.write("CALLING_DEVICE_TWO_ID = \"{extfourdeviceid}\"\n".format(
                    extfourdeviceid=self.project_config_manager.get_ext_device_id(FAREND_DEVICE_TYPE_CALLING_ONLY_2)))
                project_file.write("CALLING_DEVICE_TWO_NAME = \"{extfourdevicename}\"\n".format(
                    extfourdevicename=self.project_config_manager.get_ext_device_name(FAREND_DEVICE_TYPE_CALLING_ONLY_2)))
        except Exception as exp:
            pass
