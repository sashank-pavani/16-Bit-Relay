import os
import subprocess
import sys
from ppadb.client import Client as ADBClient
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_info

num_of_crash = 0
crash_app = None


class CaptureCrashLogs:

    def __init__(self, device_name):
        self.device_name = device_name
        client = ADBClient()
        self.device = client.device(device_name)
        self.common_keywords = CommonKeywordsClass()

    def start_capture_crash_logs(self):
        """
        This method start capturing android crash logs.
        This start one separate thread which continuously monitor android logs.
        If any crash observed, or very specific any `FATAL EXCEPTION` occur,
        this method write these exception into file.

        :return: None
        """
        try:
            robot_print_debug("Start capturing crash logs...")
            file_name = os.path.join(self.common_keywords.get_crash_log_path(), "Crash_logs.log")
            crash_cmd = "adb -s \"{}\" logcat AndroidRuntime:E *:S".format(self.device_name)
            with open(file_name, "a+", encoding='utf-8', errors='replace') as fp:
                subprocess.call(crash_cmd, stderr=subprocess.PIPE,
                                stdout=fp, shell=True)
        except OSError as os_err:
            robot_print_error("There is an exception to start capturing the crash logs,"
                              " EXCEPTION: %s" % os_err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            robot_print_error(exc_type + "\t" + fname + "\t" + exc_tb.tb_lineno)

    def lunch_crash_app(self, app):
        global num_of_crash, crash_app
        cmd = "adb -s {devicename} shell am start -n {app}".format(devicename=self.device_name,
                                                                   app=app)
        robot_print_debug("Execute: %s" % cmd)
        output = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        success, error = output.communicate()
        success = success.decode("utf-8")
        if "Starting: Intent" in success:
            robot_print_info("App start successfully  %s" % success)
        else:
            robot_print_error("Can't start app ERROR %s" % success)
        if crash_app == app:
            num_of_crash += 1
        else:
            num_of_crash -= 1
        crash_app = app

    # TODO: Need to move all related ADB action in one class
    def get_last_active_app(self):
        app = self.device.get_top_activities()[-1].package + "/" + self.device.get_top_activities()[-1].activity
        robot_print_debug("Find last active device %s" % app)
        return app

