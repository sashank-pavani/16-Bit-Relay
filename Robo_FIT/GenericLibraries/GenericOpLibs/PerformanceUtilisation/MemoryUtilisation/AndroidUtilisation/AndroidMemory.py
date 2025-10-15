""" All Lib file import which is required for this file"""
import os
import sys
from ppadb.client import Client as ADBClient
import threading
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import MEMORY
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import ANDROID_MEMORY
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info, \
    robot_print_debug

robot_print_debug(f"Import {__name__} complete")


class AndroidMemory:
    """ This class is used for taking Android Memory Logs into the file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.procrank_thread = None
        self.config_manager = ConfigurationManager()
        self.common_keywords = CommonKeywordsClass()
        self.meminfo_thread = None
        self.procstats_thread = None
        self.adb_ufs_thread = None
        self.top_cmd_thread = None
        self.adb_free_thread = None
        try:
            client = ADBClient(host='127.0.0.1', port=5037)
            self.device = client.device(self.config_manager.get_android_id())
            self.path = self.common_keywords.performance_utilization_custom_path(MEMORY, ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error("Unable to connect the Android Device to get android memory data"
                              "\nPlease check \"performance_config_file.json\" configuration file,"
                              "\nEXCEPTION: %s" % exp)

    def get_android_meminfo_data(self, test_case_name: str):
        """
        This method get the android memory data.
        Method used the android Command `adb -s <device_name> shell dumpsys meminfo`
        It create one thread which run in background and get the memory logs.
        Thread run in interval of given time(mention in performance_config_file.json).
        To stop this thread user need to call `stop_android_mem_data` method
        :param test_case_name: Test case name use to create the file.
        :return: None
        """
        meminfo_time_interval = self.config_manager.get_android_meminfo_time_interval()
        meminfo_command = self.config_manager.get_android_meminfo_command()
        self.meminfo_thread: threading.Timer = threading.Timer(meminfo_time_interval,
                                                               self.get_android_meminfo_data,
                                                               args=[test_case_name])
        self.meminfo_thread.start()
        try:
            if self.path is not None:
                file_path = os.path.join(self.path, test_case_name.split(" ")[0] + "_meminfo.log")
                with open(file_path, "a") as fp:
                    date_time = self.device.shell("date +\"%H:%M:%S\"")
                    fp.write("\nMeminfo_Cmd_Time: %s\n\n" % date_time)
                    fp.write(self.device.shell(meminfo_command))
                    fp.close()
        except RuntimeError as run_err:
            robot_print_error(f"It seems adb {self.config_manager.get_android_id()}"
                              f" devices goes offline when executing dumpsys meminfo, "
                              f"EXCEPTION: {run_err}",
                              print_in_report=True)
        except IOError as io_exp:
            robot_print_error("Error to write the android memory log, EXCEPTION: %s" % io_exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
        except Exception as exp:
            robot_print_error(f"Error to capture the adb logs for command: dumpsys meminfo, "
                              f"EXCEPTION: {exp}", print_in_report=True)

    def performance_execute_top_command(self, suite_name: str):
        """
        This method is used to capture the Android TOP command data.
        :param: suite_name: Name of the file or simply user pass the suite name
        """
        suite = suite_name.split(".")[-1]
        top_cmd = self.config_manager.get_android_top_command()
        top_time_interval = self.config_manager.get_android_top_time_interval()
        self.top_cmd_thread: threading.Timer = threading.Timer(top_time_interval,
                                                               self.performance_execute_top_command,
                                                               args=[suite])
        self.top_cmd_thread.start()
        try:
            if self.path is not None:
                file_path = os.path.join(self.path, suite.split(" ")[0] + "_top.log")
                with open(file_path, "a") as fp:
                    date_time = self.device.shell("date +\"%H:%M:%S\"")
                    fp.write("\nTop_Cmd_Time: %s\n\n" % date_time)
                    fp.write(self.device.shell(top_cmd))
                    fp.close()
        except RuntimeError as run_err:
            robot_print_error(
                f"It seems adb {self.config_manager.get_android_id()}"
                f" devices goes offline when executing '{top_cmd}', "
                f"EXCEPTION: {run_err}")
        except IOError as io_exp:
            robot_print_error("Error to write the android memory log, EXCEPTION: %s" % io_exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
        except Exception as exp:
            robot_print_error(
                f"Error to capture the adb logs for command: {top_cmd}, "
                f"EXCEPTION: {exp}")

    def capture_procrank_command_data(self, test_case_name: str):
        """
        This Function is used to get the procrank data in thread.
        : param test_case_name: file/tcname which you want to save the data
        """
        procrank_time_interval = self.config_manager.get_android_procrank_time_interval()
        procrank_cmd = self.config_manager.get_android_procrank_command()
        self.procrank_thread: threading.Timer = threading.Timer(procrank_time_interval,
                                                                self.capture_procrank_command_data,
                                                                args=[test_case_name])
        self.procrank_thread.start()
        try:
            if self.path is not None:
                file_path = os.path.join(self.path, test_case_name.split(" ")[0] + "_procrank.log")
                with open(file_path, "a") as fp:
                    date_time = self.device.shell("date +\"%H:%M:%S\"")
                    fp.write("\nProcrank_Cmd_Time: %s\n\n" % date_time)
                    fp.write(self.device.shell(procrank_cmd))
                    fp.close()
        except RuntimeError as run_err:
            robot_print_error(
                f"It seems adb {self.config_manager.get_android_id()}"
                f" devices goes offline when executing Procrank command, "
                f"EXCEPTION: {run_err}")
        except IOError as io_exp:
            robot_print_error("Error to write the android procrank log, EXCEPTION: %s" % io_exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
        except Exception as exp:
            robot_print_error(f"Error to capture the adb logs for command: procrank, "
                              f"EXCEPTION: {exp}", print_in_report=True)

    def stop_adb_mem_logs(self, log_type: str):
        """
        This method is used to stop the android memroy threads which is used by the user.
        Base of the log_type it will stop the thread.
        :param log_type: Type of the logs as below:
            1. for meminfo: "meminfo"
            2. for top : "top"
            3. for procstats: "procstats"
            4. for ufs : "ufs"
        User doesn't need to take care of these argument as these are externally handle by the framework.
        :type log_type: String
        :return: None
        :rtype:
        """
        try:
            # create the variable for save the object
            obj = None
            if log_type == "top":  # is type of top then it will stop the top command thread
                obj = self.top_cmd_thread
            elif log_type == "meminfo":  # is type of top then it will stop the top command thread
                obj = self.meminfo_thread
            elif log_type == "procstats":  # is type of top then it will stop the top command thread
                obj = self.procstats_thread
            elif log_type == "ufs":
                obj = self.adb_ufs_thread
            elif log_type == "free":
                obj = self.adb_free_thread
            elif log_type == "procrank" :
                obj = self.procrank_thread
            else:
                raise ValueError("Invalidate argument pass to stop the ADB Memory logs, "
                                 "Please check doc string of method")
            if obj is not None and type(obj) is threading.Timer:  # Check is user pass proper log_type
                robot_print_info(f"Stopping thread for {log_type}", print_in_report=True)
                obj.cancel()  # stop the given thread
            else:
                raise Exception("Its seems android memory thread object either "
                                "not created or already destroyed")
        except Exception as exp:
            robot_print_error("Can't stop the android memory thread.\nEXCEPTION: %s" % exp)

    def start_adb_procstats(self, name: str):
        """
        This method is used to capture the android procstats command data and save into file.
        :param name: Name of the file need to be set
        :type name: String
        :return: None
        :rtype: None
        """
        try:
            procstats_time_interval = self.config_manager.get_android_prostats_time_interval()
            procstats_command = self.config_manager.get_android_prostats_time_interval()
            self.procstats_thread: threading.Timer = threading.Timer(interval=procstats_time_interval,
                                                                     function=self.start_adb_procstats,
                                                                     args=[name])
            self.procstats_thread.start()
            try:
                if self.path is not None:
                    file_path = os.path.join(self.path, name.split(" ")[0] + ".log")
                    with open(file_path, "a") as fp:
                        date_time = self.device.shell("date +\"%H:%M:%S\"")
                        fp.write("\nTIME: %s\n\n" % date_time)
                        fp.write(self.device.shell(procstats_command))
                        fp.close()
            except RuntimeError as run_err:
                robot_print_error(
                    f"It seems adb {self.config_manager.get_android_id()}"
                    f" devices goes offline when executing 'dumpsys procstats --current', "
                    f"EXCEPTION: {run_err}")
            except IOError as io_exp:
                robot_print_error("Error to write the android memory log, EXCEPTION: %s" % io_exp)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
            except Exception as exp:
                robot_print_error(
                    f"Error to capture the adb logs for command: dumpsys procstats --current, "
                    f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(
                f"Error to capture the procstats data, EXCEPTION: {exp}")

    def capture_adb_ufs_data(self, name: str):
        """
        This method is  used to capture the android UFS data using 'df -k'.
        :param: name: Name of the file which should be unique otherwise overwrite the file.
        :return: None
        :rtype: None
        """
        try:
            df_time_out = self.config_manager.get_android_ufs_time_interval()
            df_command = self.config_manager.get_android_ufs_command()
            self.adb_ufs_thread: threading.Timer = threading.Timer(interval=df_time_out,
                                                                   function=self.capture_adb_ufs_data,
                                                                   args=[name])
            self.adb_ufs_thread.start()
            try:
                if self.path is not None:
                    file_path = os.path.join(self.path, name.split(" ")[0] + ".log")
                    with open(file_path, "a") as fp:
                        date_time = self.device.shell("date +\"%H:%M:%S\"")
                        fp.write("\nUfs_Cmd_Time: %s\n\n" % date_time)
                        fp.write(self.device.shell(df_command))
                        fp.close()
            except RuntimeError as run_err:
                robot_print_error(
                    f"It seems adb {self.config_manager.get_android_id()}"
                    f" devices goes offline when executing 'df -k', "
                    f"EXCEPTION: {run_err}")
            except IOError as io_exp:
                robot_print_error("Error to write the android memory log, EXCEPTION: %s" % io_exp)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
            except Exception as exp:
                robot_print_error(
                    f"Error to capture the adb logs for command: df -k, "
                    f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(
                f"Error to capture the ADB UFS df -k logs, EXCEPTION :{exp}")

    def capture_adb_free_h_data(self, name: str):
        """
        This method is  used to capture the android free data using 'free -h'.
        :param: name: Name of the file which should be unique otherwise overwrite the file.
        :return: None
        :rtype: None
        """
        try:
            free_time_out = self.config_manager.get_android_free_time_interval()
            free_cmd = self.config_manager.get_android_free_command()
            self.adb_free_thread: threading.Timer = threading.Timer(interval=free_time_out,
                                                                   function=self.capture_adb_free_h_data,
                                                                   args=[name])
            self.adb_free_thread.start()
            try:
                if self.path is not None:
                    file_path = os.path.join(self.path, name.split(" ")[0] + "_free.log")
                    with open(file_path, "a") as fp:
                        date_time = self.device.shell("date +\"%H:%M:%S\"")
                        fp.write("\nFree_Cmd_Time: %s\n\n" % date_time)
                        fp.write(self.device.shell(free_cmd))
                        fp.close()
            except RuntimeError as run_err:
                robot_print_error(
                    f"It seems adb {self.config_manager.get_android_id()}"
                    f" devices goes offline when executing 'free -h', "
                    f"EXCEPTION: {run_err}")
            except IOError as io_exp:
                robot_print_error("Error to write the android free -h log, EXCEPTION: %s" % io_exp)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                robot_print_error(exc_type + "\t" + file_name + "\t" + exc_tb.tb_lineno)
            except Exception as exp:
                robot_print_error(
                    f"Error to capture the adb logs for command: free -h, "
                    f"EXCEPTION: {exp}")
        except Exception as exp:
            robot_print_error(
                f"Error to capture the ADB free -h logs, EXCEPTION :{exp}")
