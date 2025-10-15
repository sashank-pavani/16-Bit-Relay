import re
import inspect
from robot import running, result
from robot.api.interfaces import ListenerV3
from robot.result import Message

from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.TagCountRetriever import TagCountRetriever
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info, robot_print_error, \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.listeners.RobofitExecListenerRegister import \
    RobofitExecListenerRegister
from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.CreateXmlReport import CreateXmlReport
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.BlankScreenObserver import BlankScreenObserver
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.BufferHandler import BufferHandler
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.CaptureFeed import CaptureFeed
from Robo_FIT.GenericLibraries.GenericOpLibs.UITesting.ConfigurationManager import ConfigurationManager


class RobotExecListener(ListenerV3):

    def __init__(self):
        self.comm = CommonKeywordsClass()
        self.web_cam_mng = ConfigurationManager()
        self.xml_report = CreateXmlReport.get_xml_reporting_instance()
        self.xml_report.xml_create_root()
        self.is_parsing_done = False
        # robot_print_info(f"{self.web_cam_mng.get_is_blank_screen_observed()=}")
        if self.web_cam_mng.get_is_blank_screen_observed():
            self.cam_feed = CaptureFeed()
            self.blank_screen_observer = BlankScreenObserver()
            robot_print_debug(f"Blank screen observer initialized.")
            self.buffer_handler = BufferHandler()
        else:
            robot_print_info(f"The user has set 'isObserveBlackScreen' to False in the config file, so not monitoring "
                             f"the blank screen.")
        self.tags_count = TagCountRetriever()
        self._notify_listeners("on_execution_start")
        # robot_print_info("Execution started")

    def close(self):
        self._notify_listeners("on_execution_complete")
        self.xml_report.save_xml_to_file()
        self.xml_report.parse_custom_xml_to_html()

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.comm.create_module_directory(data.name)
        self.xml_report.xml_add_module_name(data.name)
        self.xml_report.xml_add_suit_name(data.name)
        self.xml_report.create_xml_file()

    def end_suite(self, data: running.TestSuite, result: result.TestSuite):
        status = "PASS" if result.status == "PASS" else "FAIL"
        self.xml_report.xml_add_suite_end_time()
        self.xml_report.xml_add_suite_status(status)
        self.xml_report.create_xml_file()

    def start_test(self, data: running.TestCase, result: result.TestCase):
        self._notify_listeners("on_test_start", data)
        self.xml_report.xml_add_test_start_time()
        self.xml_report.xml_add_test_case(data.name, "RUNNING")
        self.xml_report.create_xml_file()

    def end_test(self, data: running.TestCase, result: result.TestCase):
        status = "PASS" if result.status == "PASS" else "FAIL"
        self._notify_listeners("on_test_end", data, result)
        self.xml_report.xml_add_test_end_time()
        self.xml_report.xml_add_test_status(status)
        self.xml_report.create_xml_file()

    def start_keyword(self, data: running.Keyword, result):
        keyword_name = data.name
        keyword_args = data.arguments
        keyword_assign = data.assign
        self.xml_report.xml_add_keyword(keyword_name, "Default", keyword_args, keyword_assign)
        self.xml_report.create_xml_file()

    def end_keyword(self, data: running.Keyword, result):
        keyword_name = data
        status = "PASS" if result.status == "PASS" else "FAIL"
        self.xml_report.xml_update_keyword_end_time()
        self.xml_report.xml_update_keyword_status(status)
        self.xml_report.create_xml_file()

    def start_user_keyword(self, data: running.Keyword, implementation, result):
        keyword_name = getattr(data, 'name', 'Unknown Keyword')
        keyword_args = getattr(data, 'args', [])
        keyword_assign = getattr(data, 'assign', [])
        self.xml_report.xml_add_keyword(keyword_name, "User", keyword_args, keyword_assign)
        self.xml_report.create_xml_file()

    def end_user_keyword(self, data: running.Keyword, implementation, result):
        keyword_name = data
        status = "PASS" if result.status == "PASS" else "FAIL"
        self.xml_report.xml_update_keyword_end_time()
        self.xml_report.xml_update_keyword_status(status)
        self.xml_report.create_xml_file()

    def start_library_keyword(self, data: running.Keyword, implementation, result):
        try:
            keyword_name = getattr(data, 'name', 'Unknown Keyword')
            keyword_args = getattr(data, 'args', [])
            keyword_assign = getattr(data, 'assign', [])
            self.xml_report.xml_add_keyword(keyword_name, "Lib", keyword_args, keyword_assign)
            self.xml_report.create_xml_file()
        except AttributeError as e:
            robot_print_error(f"Error accessing attribute: {e}")
        except Exception as e:
            robot_print_error(f"Unexpected error in start_library_keyword: {e}")

    def end_library_keyword(self, data: running.Keyword, implementation, result):
        try:
            keyword_name = data
            status = "PASS" if result.status == "PASS" else "FAIL"
            self.xml_report.xml_update_keyword_end_time()
            self.xml_report.xml_update_keyword_status(status)
            self.xml_report.create_xml_file()
        except Exception as e:
            robot_print_error(f"Error in end_library_keyword: {e}. Data: {data}, Type: {type(data)}")

    def start_invalid_keyword(self, data: running.Keyword, implementation, result):
        keyword_name = getattr(data, 'name', 'Unknown Keyword')
        keyword_args = getattr(data, 'args', [])
        keyword_assign = getattr(data, 'assign', [])
        self.xml_report.xml_add_keyword(keyword_name, "Invalid", keyword_args, keyword_assign)
        self.xml_report.create_xml_file()

    def end_invalid_keyword(self, data: running.Keyword, implementation, result):
        keyword_name = data
        status = "FAIL"
        self.xml_report.xml_update_keyword_end_time()
        self.xml_report.xml_update_keyword_status(status)
        self.xml_report.create_xml_file()

    def log_message(self, message: Message):
        message_text = self.sanitize_message(message.message)
        message_type = message.level
        if self.xml_report.current_test is not None:
            if self.xml_report.current_keyword is not None:
                self.xml_report.xml_add_message_to_keyword(message_text, message_type)
            else:
                self.xml_report.xml_add_message_to_test(message_text, message_type)
        elif self.xml_report.current_keyword is not None:
            self.xml_report.xml_add_message_to_keyword(message_text, message_type)
        else:
            self.xml_report.xml_add_general_log(message_text, message_type)

    def _notify_listeners(self, method_name, *args):
        listeners = RobofitExecListenerRegister.get_listeners()
        for listener in listeners:
            method = getattr(listener, method_name, None)
            if method:
                try:
                    # Check the number of parameters the method accepts
                    sig = inspect.signature(method)
                    method(*args[:len(sig.parameters)])
                except TypeError as e:
                    robot_print_error(f"TypeError calling {method_name} on {listener}: {e}")
                except Exception as e:
                    robot_print_error(f"Error calling {method_name} on {listener}: {e}")

    def sanitize_message(self, message_text):
        sanitized_message = re.sub(r'[\x00-\x1F\x7F]', '', message_text)
        return sanitized_message
