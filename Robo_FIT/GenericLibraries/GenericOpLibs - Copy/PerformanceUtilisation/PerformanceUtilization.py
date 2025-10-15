"""Import all required Classes"""
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CpuUtilisation.CpuQnxUtilisation.ParseCpuQnxMemory import \
    ParseCpuQnxMemory
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import *
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.MemoryUtilisation.AndroidUtilisation.AndroidMemory import AndroidMemory
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.MemoryUtilisation.AndroidUtilisation.ParseAndroidMemory import ParseAndroidMemory
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.MemoryUtilisation.QnxUtilisation.GetQnxMemoryLogs import \
    GetQnxMemoryLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CpuUtilisation.CpuAndroidUtilisation.CpuAndroidMemory import \
    CpuAndroidMemory
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CpuUtilisation.CpuAndroidUtilisation.ParseCpuAndroidMemory import \
    ParseCpuAndroidMemory
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CpuUtilisation.CpuQnxUtilisation.GetQnxCpuLogs import \
    GetQnxCpuLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.MemoryUtilisation.QnxUtilisation.ParseQnxMemory import \
    ParseQnxMemory


class PerformanceUtilization:
    """
    From this we can call all functions which is implemented for performance command utilization
    """

    def __init__(self):
        """
        This init used for initialized classes
        """
        self.suite_name = None
        self.qnx_mem = GetQnxMemoryLogs()
        self.android_mem = AndroidMemory()
        self.cpu_android_mem = CpuAndroidMemory()
        self.adb_mem_parser = ParseAndroidMemory()
        self.cpu_logger_parser = ParseCpuAndroidMemory()
        self.qnx_logger_parser = ParseQnxMemory()
        self.qnx_cpu_logger_parser = ParseCpuQnxMemory()
        self.qnx_cpu = GetQnxCpuLogs()

    def start_adb_top_logs(self, suite_name: str):
        """
        This method used to start capturing the adb top command data. User need to pass the
        time interval in config file as "topCommandInterval"
        :param suite_name: Name of file which need to be set generally user can pass suite name
        :type suite_name: String
        :return: None
        :rtype: None
        """
        try:
            self.suite_name = suite_name
            self.android_mem.performance_execute_top_command(
                suite_name=suite_name)
        except Exception as exp:
            robot_print_error(
                f"Error to start the android CPU and MEM logs, EXCEPTION: {exp}")

    def stop_adb_top_logs(self):
        """
        This method stop the adb top command logs.
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs(log_type="top")

    def parse_adb_top_log(self):
        """
        This Method is used to parse the adb top log which is created top graph and top execl file.
        :return: None
        :rtype: None
        """
        self.adb_mem_parser.parse_android_top_command_logs()

    def start_adb_meminfo_package_data(self, suite_name: str):
        """
        This method start capturing the adb -s <devicename> shell dumpsys meminfo logs
        :param suite_name: Name of the which generally suite name
        :type suite_name: String
        :return: None
        :rtype: None
        """
        try:
            self.suite_name = suite_name
            self.android_mem.get_android_meminfo_data(test_case_name=suite_name)
        except Exception as exp:
            robot_print_error(
                f"Error to start the android CPU and MEM logs, EXCEPTION: {exp}")

    def stop_adb_meminfo_package_log(self):
        """
        This method is used to stop the meminfo logs.
        It will take the package list in two way:
            1. By using argument "package_list" which is the first priority.
            2. If user not pass the argument then method will check the config file and try to get
                the package list.
            3. If not package list is provided by the user either config file or as an argument then it will only
                capture the total of all the process.
        # :param package_list: List of package, Default None
        # :type package_list: List
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs(log_type="meminfo")

    def parse_adb_meminfo_log(self):
        """
        This Method is used to parse the adb dumpsys meminfo log which is created graph and execl file.
        :return: None
        :rtype: None
        """
        self.adb_mem_parser.parse_adb_mem_pkg_logs()

    def start_adb_procrank_data(self, suite_name: str):
        """
        This method start capturing the adb -s <devicename> shell procrank logs
        :param suite_name: Name of the which generally suite name
        :type suite_name: String
        :return: None
        :rtype: None
        """
        try:
            self.suite_name = suite_name
            self.android_mem.capture_procrank_command_data(
                test_case_name=suite_name)
        except Exception as exp:
            robot_print_error(
                f"Error to start the android CPU and MEM logs, EXCEPTION: {exp}")

    def stop_adb_procrank_log(self):
        """
        This method is used to stop the procrank logs.
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs(log_type="procrank")

    def parse_adb_procrank_log(self):
        """
        This Method is used to parse the adb procrank log which is created graph and execl file.
        :return: None
        :rtype: None
        """
        self.adb_mem_parser.parse_pro_crank_commands_logs()

    def start_adb_free_data(self, suite_name: str):
        """
        This method start capturing the adb -s <devicename> shell free -h logs
        :param suite_name: Name of the which generally suite name
        :type suite_name: String
        :return: None
        :rtype: None
        """
        try:
            self.suite_name = suite_name
            self.android_mem.capture_adb_free_h_data(name=suite_name)
        except Exception as exp:
            robot_print_error(
                f"Error to start the android Free -h Logs, EXCEPTION: {exp}")

    def stop_adb_free_log(self):
        """
        This method is used to stop the free logs.
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs(log_type="free")

    def parse_adb_free_log(self):
        """
        This Method is used to parse the adb free -h log which is created graph and execl file.
        :return: None
        :rtype: None
        """
        self.adb_mem_parser.parse_android_free_command_logs()

    def start_capture_qnx_showmem_log(self):
        """
        This method is used to capture the "showmem -a" command logs.
        User need to pass the time interval for capturing the logs in config file as
        "showMemACommandInterval".
         We will recommend to use more than 30 seconds to capture the data. As QNX memory not changed that
        frequently.
        :return: None
        :rtype: None
        """
        try:
            self.qnx_mem.capture_qnx_showmem_logs()
        except Exception as exp:
            robot_print_error(
                f"Error to capture the QNX memory data, EXCEPTION: {exp}")

    def stop_qnx_mem_data(self):
        """
        This method is used to stop, parse and create the graph of showmem -a logs.
        :return: None
        :rtype: None
        """
        try:
            self.qnx_mem.stop_qnx_mem_logs(log_type="a")
        except Exception as exp:
            robot_print_error(f"Error to stop QNX mem data, EXCEPTION: {exp}",
                              print_in_report=True)

    def parse_qnx_mem_data(self):
        """
        This Method is used to parse the qnx showmem -a log which is created graph and execl file.
        :return: None
        :rtype: None
        """
        self.qnx_logger_parser.parse_qnx_showmem_log()

    def start_capture_android_cpuinfo_logs(self, name: str):
        """
        This method is used to capture the Android CPU logs by using adb shell dumpsys cpuinfo.
        User need to define the time interval in config file as "adbCpuInfoCmdInterval".
        We recommended to use time interval greater than 60 seconds as cpuinfo command data not change
        so frequently.
        :param name: Name which need to set for save the file
        :type name: String
        :return: None
        :rtype: None
        """
        self.cpu_android_mem.get_adb_cpuinfo_data(name=name)

    def stop_capture_android_cpuinfo_logs(self):
        """
        This method is used to stop, parse and create the graph of the cpuinfo logs of android.
        :return:
        :rtype:
        """
        self.cpu_android_mem.stop_adb_cpu_data()
        # self.cpu_logger_parser.parse_adb_cpuinfo_logs()

    def start_capture_android_procstats_logs(self, name: str):
        """
        This method is used to capture the adb -s <devicename> shell dumpsys proctsats data.
        :param name: Name of the file which user want to set. Ideally user can pass the suite
        ot test case name.
        :type name: String
        :return: None
        :rtype: None
        """
        self.android_mem.start_adb_procstats(name)

    def stop_capture_android_procstats_logs(self):
        """
        This method is used to stop, parse and create the graph of the android procstats logs
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs(log_type="procstats")
        # self.adb_mem_parser.parse_adb_procstats_logs(package_list=package_list)

    def start_capture_qnx_showmem_summary(self):
        """
        This method is used to capture the showmem -s logs from the QNX console.
        :return: None
        :rtype: None
        """
        self.qnx_mem.start_qnx_showmem_summary_logs()

    def stop_capture_qnx_showmem_summary(self):
        """
        This method is used to stop, parse and create the graph of qnx showmem -s command.
        :return: None
        :rtype: None
        """
        self.qnx_mem.stop_qnx_mem_logs(log_type="s")
        self.qnx_logger_parser.parse_qnx_showmem_summary_logs()

    def stop_capture_qnx_slog2_logs(self):
        """
        This method is used to stop, parse and create the graph of qnx slog2info command.
        :return: None
        :rtype: None
        """
        self.qnx_mem.stop_qnx_mem_logs(log_type="slog2")

    def start_adb_capture_ufs_data(self, name: str):
        """
        This method is used to capture the android UFS data by using df -k.
        :param: name: Name of the file which need to be set
        :return: None
        :rtype: None
        """
        self.android_mem.capture_adb_ufs_data(name=name)

    def stop_adb_ufs_data(self):
        """
        Method to stop the android UFS data
        :return: None
        :rtype: None
        """
        self.android_mem.stop_adb_mem_logs("ufs")

    def start_qnx_capture_ufs_data(self):
        """
        This method is used to capture the QNX UFS data by using df -k
        :return: None
        :rtype: None
        """
        self.qnx_mem.start_qnx_ufs_data()

    def stop_qnx_capture_ufs_data(self):
        """
        This method stop the capture QNX UFS data if started by start_qnx_capture_ufs_data(self)
        :return: None
        :rtype: None
        """
        self.qnx_mem.stop_qnx_mem_logs("ufs")

    def capture_qnx_top_data(self):
        """
        This method is used to capture the QNX top command data.
        This method execute `top -i 1 -z 40` command every given interval of time.
        :return: None
        :rtype: None
        """
        self.qnx_cpu.capture_qnx_top_logs()

    def stop_qnx_top_data(self):
        """
        This method is usd to stop the QNX Top command data if started by capture_qnx_top_data().
        :return: None
        :rtype: None
        """
        self.qnx_cpu.stop_qnx_cpu_logs("top")

    def parse_qnx_top_data(self):
        """
        This method is usd to parse top data capture by qnx
        :return: None
        :rtype: None
        """
        self.qnx_logger_parser.parse_qnx_top_data()

    def parse_all_logs(self, qnx_logs: True, mem_logs: True):
        """
        This Method is used to parse all android and qnx log file and generate the graph,execl file.
        :param qnx_logs: if you don't want parse qnx logs then give False values, default is True.
        :param mem_logs: if you don't want parse android logs then give False values, default is True.
        :return : NA
        """
        try:
            if mem_logs:
                self.adb_mem_parser.parse_adb_mem_pkg_logs()
                self.adb_mem_parser.parse_pro_crank_commands_logs()
                self.adb_mem_parser.parse_android_top_command_logs()
                self.adb_mem_parser.parse_android_free_command_logs()
                self.cpu_logger_parser.parse_android_cpu_commands_logs()
            if qnx_logs:
                self.qnx_logger_parser.parse_qnx_top_data()
                self.qnx_logger_parser.parse_qnx_showmem_log()
                self.qnx_logger_parser.parse_qnx_showmem_summary_logs()
                self.qnx_logger_parser.parse_qnx_pmem_logs()
                self.qnx_logger_parser.parse_qnx_dmem_logs()
                self.qnx_cpu_logger_parser.parse_qnx_cpu_top_data()
        except Exception as exp:
            robot_print_error(f"Not able to parse the all logs {exp}")