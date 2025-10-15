import os
import sys
from datetime import timedelta

from pywinauto.application import Application
from time import sleep
import pywinauto

from pywinauto import mouse
import win32gui
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.QualcommFlashImageLoader.ConfiguratorManager import ConfiguratorManager
from pywinauto.controls.common_controls import StatusBarWrapper, ProgressWrapper


class QfilAutomation:
    """
    This class is used to handle all the QFIL options, like load content, browser file etc.
    """

    __IS_APP_LAUNCH = False

    def __init__(self):
        """
        This is a construct of QfilAutomation, It will launch the QFIL application when
        constructor call.
        """
        self.config_manager = ConfiguratorManager()
        self.common_keywords = CommonKeywordsClass()

        self.app = self.__launch_application(path=self.config_manager.get_qfil_exe_file_path())
        robot_print_info(f"QFIL application app is: {self.app}", print_in_report=True)

    def __launch_application(self, path: str) -> pywinauto.Application:
        """
        This is a private function which is used to open the QFIL application.
        It will take the qfil.exe file path from config file
        :param path: Path of the application
        :type path: Path like object
        :return: pywinauto.Application Object
        :rtype: pywinauto.Application
        """
        try:
            if not QfilAutomation.__IS_APP_LAUNCH:
                self.exit_qfil()
                app = Application(backend='uia').start(path, wait_for_idle=False, timeout=25)
                app.window().wait("active ready", timeout=20)
                QfilAutomation.__IS_APP_LAUNCH = True
                return app
        except pywinauto.application.TimeoutError as timeout_err:
            robot_print_error(f"After waiting of 15 second still application is not ready. "
                              f"Please try again/or close all the application and then try, EXCEPTION: {timeout_err}",
                              underline=True)
        except pywinauto.application.AppStartError as application_error:
            robot_print_error(f"There is a problem starting the Application...!!!"
                              f"\nException: {application_error}")
            number_of_try = 0
            robot_print_info(f"Trying Again to open the application.")
            while number_of_try >= 3:
                self.__launch_application(self.config_manager.get_qfil_exe_file_path())
                number_of_try += 1
        except Exception as exp:
            robot_print_error(f"There is an exception to load the application...!!!"
                              f"\nException: {exp}")
            number_of_try = 0
            while number_of_try >= 3:
                self.__launch_application(self.config_manager.get_qfil_exe_file_path())
                number_of_try += 1

    def __restore_application(self):
        """
        This is a private method which is used to restore the application if it goes to background
        or not in focus
        :return: None
        :rtype: None
        """
        try:
            if self.app is not None and not self.app.window().is_active():
                self.app.window().restore()
            else:
                robot_print_debug(f"It seems QFIL application is already close and not able to restore it."
                                  f" App = {self.app}", print_in_report=True)
        except Exception as exp:
            robot_print_error(f"Error to restore the application, EXCEPTION: {exp}")

    def select_port(self):
        """
        This method is used to select the port if no COM port detected automatically
        or multiple COM port available.
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            self.app.window().child_window(auto_id="btnSelectPort").click_input()
            sleep(1)
            select_port_cancel = self.app.window().child_window(title="Select Port", auto_id="PortSelectionForm",
                                                                control_type="Window")
            select_port_cancel.child_window(title="Cancel", auto_id="btnCancel", control_type="Button").click_input()
        except Exception as exp:
            robot_print_error(f"There is an exception to select the port...!!!"
                              f"\nException: {exp}")

    @DeprecationWarning
    def set_configuration(self):
        """
        THis function is used to set the configuration.
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            config = self.app.window().child_window(auto_id="menuMain", control_type="MenuBar")
            option_config = config.child_window(title="Configuration", control_type="MenuItem", found_index=0)
            option_config.click_input()
            fire = self.app.window(best_match="FireHose Configuration", top_level_only=False)
            fire.click_input()
            sleep(2)
        except Exception as exp:
            robot_print_error(f"There is an exception to set configuration ...!!!"
                              f"\nException: {exp}")

    def load_content(self):
        """
        This method is used to load the content.xml file for Meta Build
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            path = os.path.join(os.path.join(self.common_keywords.get_root_path(), PROJECT, CRE_LIBRARIES,
                                             CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_INPUT_BUILD_DIR),
                                self.config_manager.get_qfil_load_content_file_path())
            robot_print_debug(f"Loading contents.xml file from: {path}")
            lc = self.app.window(best_match="Load Content ...", top_level_only=False)
            robot_print_debug(f"lc: {lc}", print_in_report=True)
            lc.click_input()
            sleep(3)
            open_window = self.app.window(best_match="Open", top_level_only=False)
            file_name = open_window.child_window(title="File name:", auto_id="1148", control_type="ComboBox")
            file_name.child_window(title="File name:", auto_id="1148", control_type="Edit").set_edit_text(path)
            open_window.child_window(title="Open", auto_id="1", control_type="Button").click_input()
        except Exception as exp:
            robot_print_error(f"There is an exception to load the content...!!!\nException: {exp}")

    def capture_qfil_screenshot(self, name: str):
        """
        This function is used to save the screenshot and save with given name
        :param name: Name of the file
        :type name: String
        :return: None
        :rtype: None
        """
        try:
            path = os.path.join(self.common_keywords.get_qfil_log_file_path(), f"{name}.png")
            self.app.window().capture_as_image().save(path)
        except Exception as exp:
            robot_print_error(f"Error to capture the QFIL screenshot, EXCEPTION; {exp}", print_in_report=True)

    def download_content(self) -> bool:
        """
        This method is used to click on download content. If button is disable it will return False.
        Otherwise it will click on the button
        :return: True if click on Download button, otherwise False
        :rtype: bool
        """
        try:
            download = self.app.window().child_window(auto_id="FireHoseDownloadTab")
            download_button = download.child_window(title="Download Content", auto_id="btnDownload")
            self.capture_qfil_screenshot("download_button.png")
            if download_button.is_enabled():
                robot_print_info("Ready too download the Content")
                download_button.click_input()
                return True
            else:
                robot_print_error("It seems download button is disable which means some issue with the build path,"
                                  " or QFIL port disconnected.")
                return False
        except Exception as exp:
            robot_print_error("There may be a problem with Download Content...!!!\nException: %s" % exp)
            return False

    def browse_programmer_path(self):
        """
        This method is used to load or browse the .elf file.
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            path = os.path.join(os.path.join(self.common_keywords.get_root_path(), PROJECT, CRE_LIBRARIES,
                                             CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_INPUT_BUILD_DIR),
                                self.config_manager.get_qfil_browser_file_path())
            robot_print_debug(f"Loading .elf file from: {path}")
            browser_window = self.app.window().child_window(title="Browse ...", auto_id="btnBrowseProgrammer")
            browser_window.click_input()
            sleep(3)
            open_window = self.app.window(best_match="Open", top_level_only=False)
            file_name = open_window.child_window(title="File name:", auto_id="1148", control_type="ComboBox")
            file_name.child_window(title="File name:", auto_id="1148", control_type="Edit").set_edit_text(path)
            open_window.child_window(title="Open", auto_id="1", control_type="Button").click_input()
        except Exception as exp:
            robot_print_error(f"There may be a problem to Browser File from target...!!!"
                              f"\nException: {exp}")

    def flat_build(self):
        """
        This method is use to select the Flat Build option.
        :return: None
        :rtype: None
        """
        try:
            flat_build = self.app.window(best_match="Flat Build", top_level_only=False)
            flat_build.click_input()
        except Exception as exp:
            robot_print_error(f"There may be a problem to select the Flat Build...!!!"
                              f"\nException: {exp}")

    def meta_build(self):
        """
        This method is used to select the Meta Build option.
        :return: None
        :rtype: None
        """
        try:
            mate_build = self.app.window(best_match="Meta Build", top_level_only=False)
            mate_build.click_input()
        except Exception as exp:
            robot_print_error(f"There may be a problem to select the Meta Build...!!!"
                              f"\nException: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def set_available_meta_build_type(self, build_type: str = "emmc"):
        """
        This method is use to select the meta build type as emmc
        :param build_type: Used to set the type, By Default it will select emmc
        :type build_type: String
        :return: None
        :rtype: None
        """
        try:
            c = self.app.window().child_window(auto_id="FireHoseDownloadTab")
            c.child_window(auto_id="cmbProductFlavors").select("6155_la")
            sleep(1)
            c.child_window(auto_id="cmbMetaBuildStorageType").select(build_type)
        except Exception as exp:
            robot_print_error(f"There may be a problem to Set 'Available Meta Build Type'...!!!"
                              f"\nException: {exp}")

    def check_port(self) -> bool:
        """
        This method is used to check the COM port of QFIL, If 'No Port Available' is shown on
        QFIL then it will return False, else True
        :return: True if COM port detected, otherwise False
        :rtype: bool
        """
        try:
            port_label = self.app.window().child_window(auto_id="lblSelectPort")
            text = port_label.window_text()
            if text == "No Port Available":
                robot_print_error("Flashing process is STOPPED, because No Port Available")
                robot_print_error("Please check the PIN's and try again")
                self.capture_qfil_screenshot("no_port.png")
                return False  # TODO: Need to change to False
            return True
        except Exception as exp:
            robot_print_error(f"There is an problem to checking the port...!!!"
                              f"\nExceptions: {exp}")
            return False

    def set_storage_type(self):
        """
        THis method is used to set the storage type
        :return: None
        :rtype: None
        """
        try:
            st = self.app.window().child_window(title="statusStrip", auto_id="statMain", control_type="StatusBar")
            value = st.child_window(control_type="MenuItem", found_index=0)
            value.click_input()
            em = value.child_window(control_type="MenuItem", found_index=3)
            robot_print_debug(f"em {em}")
            em.click_input()
            # self.app.window(best_match="Storage Type:", top_level_only=False).print_control_identifiers()
        except Exception as exp:
            robot_print_error(f"There may be a problem to set 'Storage Type'...!!!"
                              f"\nException: {exp}")

    def get_status(self) -> str:
        """
        This method is used to save the QFIL logs.
        It will save at <homepath>/<reportpath>/QFILLogs/<logfilename>
        :return: Path of the file where file store
        :rtype: String
        """
        try:
            self.__restore_application()
            path = os.path.join(self.common_keywords.get_qfil_log_file_path(), self.config_manager.get_qfil_log_path())
            status = self.app.window().child_window(auto_id="infoLog")
            status_info = status.child_window(auto_id="qualInfoBox", control_type="Pane")
            status_info.click_input(button='right')
            save_info = self.app.window(best_match="Save Log", top_level_only=False)
            robot_print_debug(f"save_info: {save_info}")
            save_info.click_input()
            sleep(2)
            save_as = self.app.window(best_match="Save as", top_level_only=False)
            file_name = save_as.child_window(title="File name:", auto_id="FileNameControlHost", control_type="ComboBox")
            file_name.child_window(title="File name:", auto_id="1001", control_type="Edit").set_edit_text(path)
            # save_as.print_control_identifiers()
            save_as.child_window(title="Save", auto_id="1", control_type="Button").click_input()
            return path
        except Exception as exp:
            robot_print_error(f"There may be a problem to get the status and store into file...!!!"
                              f"\nException: {exp}")

    def progress_bar(self):
        """
        This method is used to capture the progress bar status
        :return: count of progress bar
        :rtype: String
        """
        try:
            a = self.app.window().child_window(auto_id="progPercentage", control_type="Pane")
            logs = self.app.window().child_window(auto_id="infoLog", control_type="Pane")
            percentage = StatusBarWrapper(a).get_count()
            # TODO: It seems QFIL not using Status or percentage bar. So this method may now work.
            return percentage
        except Exception as exp:
            robot_print_error(f"There may be a problem to get the data from the progress bar...!!!"
                              f"\nException: {exp}")
            return -1

    def exit_qfil(self):
        """
        THis method is used to close the QFIL application is open
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            if self.app is not None:
                self.app.window().child_window(title="Exit", auto_id="btnExit").click_input()
                QfilAutomation.__IS_APP_LAUNCH = False
            else:
                robot_print_debug(f"It seems application is already in close state.")
        except Exception as exp:
            robot_print_error(f"There may be a problem to exit the QFIL application...!!!"
                              f"\nException: {exp}")

    def provision_select_from_configuration(self) -> bool:
        """
        This method is use dto set the configuration for Provisioning
        :return: True if provisioning done
        :rtype: Bool
        """
        try:
            self.__restore_application()
            config = self.app.window().child_window(auto_id="menuMain", control_type="MenuBar")
            config1 = config.child_window(title="Configuration", control_type="MenuItem")
            config1.click_input()
            sleep(2)
            (x, y) = win32gui.GetCursorPos()
            robot_print_debug(f"{x, y}")
            mouse.click(button='left', coords=(x, y + 20))
            sleep(1)
            opetions = self.app.window().child_window(title="Download Configuration", auto_id="ConfigurationForm",
                                                      control_type="Window")
            options1 = opetions.child_window(title="Device Type", auto_id="lblDeviceType", control_type="Text")
            options1.click_input()
            (x, y) = win32gui.GetCursorPos()
            robot_print_debug(f"{x, y}")
            mouse.click(button='left', coords=(x + 100, y))
            (x, y) = win32gui.GetCursorPos()
            robot_print_debug(f"{x, y}")
            mouse.click(button='left', coords=(x, y + 50))
            provision_cb = opetions.child_window(title="Provision", auto_id="chkProvision", control_type="CheckBox")
            provision_cb.click_input()
            ok = opetions.child_window(title="OK", auto_id="btnOK", control_type="Button")
            ok.click_input()
            provision_title = self.app.window().child_window(auto_id="FireHoseDownloadTab", control_type="Pane") \
                .child_window(title="Provision", auto_id="lblBuildType", control_type="Text")
            provision_title.click_input()
            return True
        except Exception as exp:
            robot_print_error(f"Error to select the Provision from settings, EXCEPTION :{exp}")
            return False

    def provision_browser_xml(self):
        """
        This method is used to select the Provision XML file form user given path.
        :return: None
        :rtype: None
        """
        try:
            self.__restore_application()
            browser = self.app.window().child_window(title="Browse ...", auto_id="btnBrowseSearchPath",
                                                     control_type="Button")
            browser.click_input()
            sleep(3)
            path = os.path.join(os.path.join(self.common_keywords.get_root_path(), PROJECT, CRE_LIBRARIES,
                                             CRE_EXTERNAL_FILES, CRE_INPUT_FILES, CRE_INPUT_BUILD_DIR),
                                self.config_manager.get_provision_xml_path())
            robot_print_debug(f"Provision XML path: {path}")
            open_window = self.app.window(best_match="Open", top_level_only=False)
            file_name = open_window.child_window(title="File name:", auto_id="1148", control_type="ComboBox")
            file_name.child_window(title="File name:", auto_id="1148", control_type="Edit").set_edit_text(path)
            open_window.child_window(title="Open", auto_id="1", control_type="Button").click_input()
        except Exception as exp:
            robot_print_error(f"Error to load the Provision XML file, EXCEPTION: {exp}")

    def click_provision_button(self) -> bool:
        """
        This button is used to click on Provision Button to start the provisioning
        :return: True if click otherwise False
        :rtype: bool
        """
        try:
            download = self.app.window().child_window(title="Provision", auto_id="btnDownload", control_type="Button")
            download_button = download.is_enabled()
            self.capture_qfil_screenshot("provision_button_status.png")
            if download_button:
                robot_print_info("Ready too provision the Content")
                download.clicl_input()
                return True
            else:
                robot_print_error("It seems provision button is disable which means some issue with the build path,"
                                  " or QFIL port disconnected.")
                return False
        except Exception as exp:
            robot_print_error(f"Error to click on provision button to start flashing, EXCEPTION: {exp}")

    def select_product_flavors(self, flavors: str):
        """
        This method select the build product flavors.
        :param flavors: Product flavors which need to be select.
            It should be "8155_la" and "6155_la". It only needed when wrong value mention in
            content.xml file.
        :type flavors: String
        :return: None
        :rtype: None
        """
        try:
            product_flavour_option = self.app.window().child_window(auto_id="cmbProductFlavors")
            product_flavour_option.select(flavors)
            return True
        except Exception as exp:
            robot_print_error(f"Error to select the product flavors, EXCEPTION: {exp}")
            return False
