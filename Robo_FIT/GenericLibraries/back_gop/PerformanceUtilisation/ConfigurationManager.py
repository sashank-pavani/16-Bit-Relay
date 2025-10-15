"""Config Manger Handler"""

from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationReader import ConfiguratorReader
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error

"""This class is used for handle json config file"""


class ConfigurationManager:
    """
    This Class is used to generate function for command and interval time
    """
    def __init__(self):
        """
        Constructor of ConfigurationManager
        """
        self.config_file = ConfiguratorReader()

    def get_android_id(self) -> str:
        """
        This method return the android id for performance utilization
        :return: string value of Android ID
        """
        return self.config_file.read_string("androidId")

    def get_android_top_time_interval(self) -> float:
        """
        This method provide the top time interval.
        This interval is used to get the top data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['top']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of top command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_android_top_command(self) -> str:
        """
        This method provide the android top command.
        This command is used to get the top data from android.
        After given command program will go to DUMP the data.
        :return: String value of the command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['top']["cmd"]
            return str(cmd if cmd != "" else "top")
        except Exception as exp:
            robot_print_error(f"Error to get the top command, "
                              f"Use default top command, EXCEPTION: {exp}")
            return "top"

    def get_android_meminfo_time_interval(self) -> float:
        """
        This method provide the meminfo time interval.
        This interval is used to get the meminfo data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['meminfo']["timeinterval"]
            return float(interval if interval != "" else 30.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of dumpsys meminfo command, "
                              f"Use default 30 seconds, EXCEPTION: {exp}")
            return 30.0

    def get_android_meminfo_command(self) -> str:
        """
        This method provide the meminfo command eg -: dumpsys meminfo.
        This command is used to get the meminfo data from android.
        After given command program will go to DUMP the data.
        :return: String Value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['meminfo']["cmd"]
            return str(cmd if cmd != "" else "dumpsys meminfo")
        except Exception as exp:
            robot_print_error(f"Error to get the meminfo command, "
                              f"Use default dumpsys meminfo command, EXCEPTION: {exp}")
            return "dumpsys meminfo"

    def get_android_procrank_time_interval(self) -> float:
        """
        This method provide the procrank time interval.
        This command is used to get the procrank data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['procrank']["timeinterval"]
            return float(interval if interval != "" else 40.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of procrank command, "
                              f"Use default 40 seconds, EXCEPTION: {exp}")
            return 40.0

    def get_android_procrank_command(self) -> str:
        """
        This method provide the Procrank command
        This cmd is used to get the procrnak data from android.
        After given interval program will go to DUMP the data.
        :return: String Value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['procrank']["cmd"]
            return str(cmd if cmd != "" else "procrank")
        except Exception as exp:
            robot_print_error(f"Error to get the procrank command, "
                              f"Use default procrank command, EXCEPTION: {exp}")
            return "procrank"

    def get_android_free_time_interval(self) -> float:
        """
        This method provide the Free command time interval.
        This interval is used to get the free data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['free']["timeinterval"]
            return float(interval if interval != "" else 20.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of free command, "
                              f"Use default 20 seconds, EXCEPTION: {exp}")
            return 20.0

    def get_android_free_command(self) -> str:
        """
        This method provide the free command in adb.
        This command is used to get the free data from android.
        After given cmd program will go to DUMP the data.
        :return: String value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['free']["cmd"]
            return str(cmd if cmd != "" else "free -h")
        except Exception as exp:
            robot_print_error(f"Error to get the free command, "
                              f"Use default command is free -h, EXCEPTION: {exp}")
            return "free -h"

    def get_android_prostats_time_interval(self) -> float:
        """
        This method provide the prostats time interval.
        This interval is used to get the prostats data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['prostats']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of Prostats command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_android_prostats_command(self) -> str:
        """
        This method provide the prostats command.
        This command is used to get the prostats data from android.
        After given command, program will go to DUMP the data.
        :return: string value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['prostats']["cmd"]
            return str(cmd if cmd != "" else "prostats")
        except Exception as exp:
            robot_print_error(f"Error to get the prostats command, "
                              f"Use default command is prostats, EXCEPTION: {exp}")
            return "prostats"

    def get_android_ufs_time_interval(self) -> float:
        """
        This method provide the ufs time interval.
        This interval is used to get the meminfo data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['adbUFS']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of ufs command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_android_ufs_command(self) -> str:
        """
        This method provide the ufs command.
        This command is used to get the UFS data from android.
        After given command program will go to DUMP the data.
        :return: String value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['adbUFS']["cmd"]
            return str(cmd if cmd != "" else "df -k")
        except Exception as exp:
            robot_print_error(f"Error to get the ufs command, "
                              f"Use default command is df -k, EXCEPTION: {exp}")
            return "df -k"

    def get_android_cpuinfo_time_interval(self) -> float:
        """
        This method provide the cpuinfo time interval.
        This interval is used to get the cpuinfo data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['adbcpuinfo']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of cpuinfo command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_android_cpuinfo_command(self) -> str:
        """
        This method provide the cpuinfo command.
        This command is used to get the cpuinfo data from android.
        After given command, program will go to DUMP the data.
        :return: string value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['adbcpuinfo']["cmd"]
            return str(cmd if cmd != "" else "cpuinfo")
        except Exception as exp:
            robot_print_error(f"Error to get the cpuinfo command, "
                              f"Use default command is cpuinfo, EXCEPTION: {exp}")
            return "dumpsys cpuinfo"

    def get_qnx_top_time_interval(self) -> float:
        """
        This method provide the qnx top time interval.
        This interval is used to get the qnx top data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['qnxTop']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of qnx top command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_qnx_top_command(self) -> str:
        """
        This method provide the QNX top command.
        This interval is used to get the qnx top data from android.
        After given command on qnx program will go to DUMP the data.
        :return: String Value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['qnxTop']["cmd"]
            return str(cmd if cmd != "" else "top")
        except Exception as exp:
            robot_print_error(f"Error to get the qnx top command, "
                              f"Use default top command, EXCEPTION: {exp}")
            return "top"

    def get_qnx_showmem_a_time_interval(self) -> float:
        """
        This method provide the qnx showmem -a time interval.
        This interval is used to get the qnx showmem -a data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['showmemA']["timeinterval"]
            return float(interval if interval != "" else 30.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of showmem -a command, "
                              f"Use default 30 seconds, EXCEPTION: {exp}")
            return 30.0

    def get_qnx_showmem_a_command(self) -> str:
        """
        This method provide the showmem -a command
        This command is used to get the showmem -a data from android.
        After given command program will go to DUMP the data.
        :return: String value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['showmemA']["cmd"]
            return str(cmd if cmd != "" else "showmem -a")
        except Exception as exp:
            robot_print_error(f"Error to get the showmem -a command, "
                              f"Use default showmem -a command, EXCEPTION: {exp}")
            return "showmem -a"

    def get_qnx_showmem_s_time_interval(self) -> float:
        """
        This method provide the qnx showmem -s time interval.
        This interval is used to get the qnx showmem -s data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['showmemS']["timeinterval"]
            return float(interval if interval != "" else 60.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of showmem -s command, "
                              f"Use default 60 seconds, EXCEPTION: {exp}")
            return 60.0

    def get_qnx_showmem_s_command(self) -> str:
        """
        This method provide the showmem -s command
        This command is used to get the showmem -s data from android.
        After given command program will go to DUMP the data.
        :return: String value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['showmemS']["cmd"]
            return str(cmd if cmd != "" else "showmem -s")
        except Exception as exp:
            robot_print_error(f"Error to get the showmem -s command, "
                              f"Use default showmem -s command, EXCEPTION: {exp}")
            return "showmem -s"

    def get_qnx_ufs_time_interval(self) -> float:
        """
        This method provide the ufs time interval.
        This interval is used to get the ufs data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['qnxUFS']["timeinterval"]
            return float(interval if interval != "" else 5.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of ufs command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 5.0

    def get_qnx_ufs_command(self) -> str:
        """
        This method provide the ufs command.
        This interval is used to get the ufs data from android.
        After given interval program will go to DUMP the data.
        :return: String Value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['qnxUFS']["cmd"]
            return str(cmd if cmd != "" else "df -h")
        except Exception as exp:
            robot_print_error(f"Error to get the ufs command, "
                              f"Use default command is df -h, EXCEPTION: {exp}")
            return "df -h"

    def get_qnx_slog_interval(self) -> float:
        """
        This method provide the ufs time interval.
        This interval is used to get the ufs data from android.
        After given interval program will go to DUMP the data.
        :return: Float value of Time Interval
        """
        try:
            interval = self.config_file.read_list('performanceCommands')['qnxslog2info']["timeinterval"]
            return float(interval if interval != "" else 30.0)
        except Exception as exp:
            robot_print_error(f"Error to get the time interval of slog2info command, "
                              f"Use default 5 seconds, EXCEPTION: {exp}")
            return 30.0

    def get_qnx_slog2_command(self) -> str:
        """
        This method provide the ufs command.
        This interval is used to get the ufs data from android.
        After given interval program will go to DUMP the data.
        :return: String Value of command
        """
        try:
            cmd = self.config_file.read_list('performanceCommands')['qnxslog2info']["cmd"]
            return str(cmd if cmd != "" else "slog2info")
        except Exception as exp:
            robot_print_error(f"Error to get the ufs command, "
                              f"Use default command is df -h, EXCEPTION: {exp}")
            return "slog2info"


