""" All Lib file import which is required for this file"""

import os
from datetime import datetime
from ppadb.client import Client as ADBClient
import threading
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import *
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error


class CpuAndroidMemory:
    """ This class is used for taking CPU Android Memory Logs into the file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.config_manager = ConfigurationManager()
        self.time_interval = self.config_manager.get_android_cpuinfo_time_interval()
        self.common_keywords = CommonKeywordsClass()
        self.thread_obj = None
        try:
            client = ADBClient(host='127.0.0.1', port=5037)
            self.device = client.device(self.config_manager.get_android_id())
            self.path = self.common_keywords.performance_utilization_custom_path(CPU, ANDROID_CPUINFO)
        except Exception as exp:
            robot_print_error("Unable to connect the Android Device to get android memory data"
                              "\nPlease check \"performance_config_file.json\" configuration file,"
                              "\nEXCEPTION: %s" % exp)

    def get_adb_cpuinfo_data(self, name: str):
        """
        This method is used to capture the Android CPU logs by using adb shell dumpsys cpuinfo.
        User need to define the time interval in config file as "adbCpuInfoCmdInterval".
        We recommended to use time interval greater than 60 seconds as cpuinfo command data not change
        so frequently.
        :param name: Name which need to set for save the file
        :return: None
        """
        try:
            name = name if name != "" else f"CPUINFO_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}"
            command = self.config_manager.get_android_cpuinfo_command()
            self.thread_obj: threading.Timer = threading.Timer(self.time_interval,
                                                               self.get_adb_cpuinfo_data,
                                                               args=[name])
            self.thread_obj.start()
            try:
                if self.path is not None:
                    file_path = os.path.join(os.path.join(self.path, name.split(" ")[0] + ".log"))
                    with open(file_path, "a") as fp:
                        date_time = self.device.shell("date +\"%H:%M:%S\"")
                        fp.write("\nCPUinfo_Cmd_Time: %s\n\n" % date_time)
                        fp.write(self.device.shell(command))
                        fp.close()
            except RuntimeError as run_err:
                robot_print_error(f"It seems device is offline while capturing the adb cpuinfo logs, "
                                  f"EXCEPTION: {run_err}", print_in_report=True)
            except Exception as exp:
                robot_print_error(f"Error to capture the ADB cpuinfo data, EXCEPTION: {exp}",
                                  print_in_report=True)

        except Exception as exp:
            robot_print_error(f"Error to capture the ADB cpuinfo data, EXCEPTION: {exp}",
                              print_in_report=True)

    def stop_adb_cpu_data(self):
        """
        This method is used to stop the android cpu thread which used to get the cpu utilization logs.
        :return: None
        """
        try:
            if self.thread_obj is not None and type(self.thread_obj) is threading.Timer:
                self.thread_obj.cancel()
            else:
                raise Exception("Its seems android memory thread object either "
                                "not created or already destroyed")
        except Exception as exp:
            robot_print_error("Can't stop the android memory thread.\nEXCEPTION: %s" % exp)
