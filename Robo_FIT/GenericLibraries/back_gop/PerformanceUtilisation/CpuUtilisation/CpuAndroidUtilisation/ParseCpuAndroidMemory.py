""" All Lib file import which is required for this file"""
import re
import sys
import pandas as pd
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import *
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.ExtractPerformanceLogs import \
    ExtractPerformanceLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.LogParserClass import LogParserClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error

"""Below dataset used for parse the android top log with help of Regular Expression"""
LOG_FILE_CONTAINS = "top"
LOG_FILE_EXTENSION = ".log"
ANDROID_CPU_DATASET = [
    LogParserClass("Top_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){10}", None, [-1, -4], "pkg", False, True)
]
DUMPSYS_CONTAIN = "CPUINFO_"
DUMPSYSINFO_CPU_DATASET = [
    LogParserClass("CPUinfo_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("Load:\s\d\S+", ":", 1, "Load(last 1 minutes)", False),
    LogParserClass("Load:\s\d\S+\s\S\s\S+", None, -1, "Load(last 5 minutes)", False),
    LogParserClass("Load:\s\d\S+\s\S\s\S+\s\S\s\S+", None, -1, "Load(last 15 minutes)", False),
    LogParserClass("\d+%\sTOTAL:", "%", 0, "Total", False)
]


class ParseCpuAndroidMemory:
    """ This class is used for Parse CPU Android Memory Logs into the execl and graph"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.common_keywords = CommonKeywordsClass()
        self.path = self.common_keywords.performance_utilization_custom_path(CPU, ANROID_CPU)
        self.extract_log_class = ExtractPerformanceLogs()

    def parse_android_cpu_commands_logs(self):
        """
        This method parse the memory logs which is taken by `AndroidMemory.performance_execute_top_command(test_case_name: str)`
        method. This creates on DataFrame and save this into excel file and create graph.
        :except Generic Exception.
        :return: None
        """
        try:
            path = self.common_keywords.performance_utilization_custom_path(MEMORY, ANDROID_MEMORY)
            cpu_df = self.extract_log_class.extract_logs_from_path(path, LOG_FILE_CONTAINS,
                                                                   LOG_FILE_EXTENSION,
                                                                   ANDROID_CPU_DATASET, False)
            for file in cpu_df:
                cpu_df[file] = cpu_df[file].fillna(0)
                self.__plot_android_cpu_package_wise_graph(cpu_df[file], "Android_CPU_Data", file)
                new_column_names = {col: re.sub(r'[^\w\s]', '_', col) for col in
                                    cpu_df[file].columns}
                cpu_df[file].rename(columns=new_column_names, inplace=True)
            self.extract_log_class.save_df_into_execl(i_dict_df=cpu_df, i_out_file_name="Android_CPU_Data",
                                                      sub_folder=ANROID_CPU, folder_name=CPU)
        except Exception as exp:
            robot_print_error("Can't parse android cpu logs.\nEXCEPTION: %s" % exp)
            robot_print_error("Can't parse android cpu logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(exc_type,
                  file_name, exc_tb.tb_lineno)

    def parse_android_dumpsys_cpuinfo_commands_logs(self):
        """
        This method parse the memory logs which is taken by `.(test_case_name: str)`
        method. This creates on DataFrame and save this into excel file and create graph.
        :except Generic Exception.
        :return: None
        """
        try:
            path = self.common_keywords.performance_utilization_custom_path(CPU, ANDROID_CPUINFO)
            cpu_df = self.extract_log_class.extract_logs_from_path(path, DUMPSYS_CONTAIN,
                                                                   LOG_FILE_EXTENSION,
                                                                   DUMPSYSINFO_CPU_DATASET, False)
            for file in cpu_df:
                cpu_df[file] = cpu_df[file].fillna(0)
            self.extract_log_class.save_df_into_execl(i_dict_df=cpu_df, i_out_file_name="Android_CPUINFO_Data",
                                                      sub_folder=ANROID_CPU, folder_name=CPU)
        except Exception as exp:
            robot_print_error("Can't parse android cpuinfo logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(exc_type,file_name, exc_tb.tb_lineno)

    def __plot_android_cpu_package_wise_graph(self, df: pd.DataFrame, suite: str, title: str = None):
        """
        This method is used to create the graph for cpu packages which is get from "top -i 1" command.
        :param df: data frame of given command
        :type df: pd.DataFrame
        :param suite: Name of the graph which need to be set
        :type suite: String
        :param title: Name of Title of graph.
        :type title: String
        :return: None
        :rtype: None
        """
        try:
            import plotly.graph_objects as go
            packages_names = [pkg_name for pkg_name in df.columns if
                              "pkg" in pkg_name and "top" not in pkg_name and "adbd" not in pkg_name and "procrank" not in pkg_name]
            df[packages_names] = df[packages_names].astype(float)
            meminfo_table = pd.pivot_table(df, values=packages_names,
                                           index="1.Time")
            packages_names_filtered = [pkg_name for pkg_name in packages_names
                                       if df[pkg_name].mean() > 5.0]
            data = []
            p = None
            for i in packages_names_filtered:
                robot_print_debug(f"Ploting for package: {i}")
                if i == "1.Time":
                    p = go.Scatter(x=meminfo_table.index, y=meminfo_table[i], mode="lines", name=i)
                else:
                    p = go.Scatter(x=meminfo_table.index, y=meminfo_table[i], mode="lines", name=i,
                                   visible="legendonly")
                data.append(p)
            fig = go.Figure(data)
            title = title if title is not None else "Android CPU"
            fig.update_layout(title_text=f"Android CPU {title}",
                              title_font_size=30,
                              xaxis_title="<b>Time<b>",
                              yaxis_title="<b>Total CPU Utilization in %<b>"
                              )
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for cpu package wise data, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(f"Error at: {exc_type, file_name, exc_tb.tb_lineno}")

