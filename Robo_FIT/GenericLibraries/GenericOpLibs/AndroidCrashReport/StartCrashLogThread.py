from time import sleep
from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidCrashReport.CrashLogThread import CrashLogsThread
from Robo_FIT.GenericLibraries.GenericOpLibs.AndroidCrashReport.ParseCrashLogs import ParseCrashLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class StartCrashLogThread:

    def __init__(self, device_name):
        self.device_name = device_name
        self.crash_log_thread = CrashLogsThread.get_crash_log_thread_instance(device_name=self.device_name)
        self.__run_thread()
        self.parse_crash_logs = ParseCrashLogs(device_name)

    def __run_thread(self):
        if not self.crash_log_thread.is_alive():
            self.crash_log_thread.start()

    def start_crash_log_thread(self, test_case_name: str):
        try:
            if self.crash_log_thread.is_alive():
                robot_print_debug("Start crash log thread...")
                self.parse_crash_logs.start_parsing_crash_log_file(test_case_name=test_case_name)
            else:
                robot_print_debug("Restart Crash log thread...")
                self.crash_log_thread.start()
                sleep(10)
                if self.crash_log_thread.is_alive():
                    self.parse_crash_logs.read_line_number_of_file()
                    sleep(10)
        except Exception as exp:
            robot_print_error("Error to start crash logs %s " % exp)

    def set_last_active_app(self):
        self.parse_crash_logs.set_current_app()