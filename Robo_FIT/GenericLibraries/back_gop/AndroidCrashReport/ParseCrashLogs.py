import os
import sys
from Robo_FIT.GenericLibraries.GenericOpLibs.Reporting.CreateXmlReport import CreateXmlReport
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidCrashReport.CaptureCrashLogs import CaptureCrashLogs

line_number = -1
APP = None


class ParseCrashLogs:

    def __init__(self, device_name):
        self.common_keywords = CommonKeywordsClass()
        self.xml_report = CreateXmlReport.get_xml_reporting_instance()
        self.capture_crash_log = CaptureCrashLogs(device_name=device_name)

    def start_parsing_crash_log_file(self, test_case_name: str):
        try:
            global line_number, APP
            tname = test_case_name.split(" ")[0].strip()
            path = self.common_keywords.get_crash_log_path()
            robot_print_debug("Crash logs path: %s " % path)
            file_name = os.path.join(path, "Crash_logs.log")
            is_crash = False
            robot_print_debug("Start parsing crash log file...")
            with open(file_name, "r") as fp:
                crash_packages = []
                is_crash_observed = False
                for num, line in enumerate(fp):
                    if num > line_number:
                        if "FATAL EXCEPTION" in line:
                            is_crash = True
                            is_crash_observed = True
                        if "Process:" in line and "PID:" in line and is_crash:
                            crash_package_name = line.split("Process:")[1].split(",")[0].strip()
                            crash_packages.append(crash_package_name)
                            is_crash = False
                if is_crash_observed:
                    self.xml_report.xml_add_crash_data(test_case_name=tname, package_list=str(crash_packages))
                if APP is not None:
                    robot_print_debug("Wait for start app")
                    self.capture_crash_log.lunch_crash_app(app=APP)
                    robot_print_debug("App Strat")
                else:
                    robot_print_debug("NO APP CRASH RECORDED")
                is_crash_observed = False
                line_number = num
                robot_print_debug("Number of line is : %s" % str(line_number))
                robot_print_debug("Stop parsing crash log file...")
                robot_print_debug(line_number)
        except IOError as io_err:
            robot_print_error("Either Crash log file is no present in the location, or error to read file"
                              "EXCEPTION: %s" % io_err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            robot_print_error(exc_type + "\t" + fname + "\t" + exc_tb.tb_lineno)
        except Exception as exp:
            robot_print_error("There is an error to parse the crash log file\t"
                              "EXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            robot_print_error(exc_type + "\t" + fname + "\t" + exc_tb.tb_lineno)
        finally:
            fp.close()

    def read_line_number_of_file(self):
        try:
            global line_number
            path = self.common_keywords.get_crash_log_path()
            robot_print_debug("Crash logs path:  ", path)
            file_name = os.path.join(path, "Crash_logs.log")
            with open(file_name, "r", encoding='utf-8', errors='replace')as fp:
                for i, line in enumerate(fp):
                    pass
                line_number = i
            fp.close()
            robot_print_debug("Line number while reading file : %s" % line_number)
        except OSError as oserr:
            robot_print_error("Error to read the Crash Log File, EXCEPTION : %s" % oserr)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            robot_print_error(exc_type + "\t" + fname + "\t" + exc_tb.tb_lineno)

    def set_current_app(self):
        global APP
        APP = self.capture_crash_log.get_last_active_app()
        robot_print_debug("CURRENT APP %s" % APP)
