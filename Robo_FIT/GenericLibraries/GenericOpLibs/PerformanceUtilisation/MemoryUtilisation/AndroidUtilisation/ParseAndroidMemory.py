""" All Lib file import which is required for this file"""
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.ExtractPerformanceLogs import \
    ExtractPerformanceLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_error
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import \
    MEMORY
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import \
    ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import \
    ANDROID_MEMORY
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import \
    CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.LogParserClass import \
    LogParserClass
import pandas as pd
import os
import sys

"""Below datasets used for parse the android top/meminfo/free/procrank log with help of Regular Expression"""

LOG_FILE_CONTAINS = "top"
LOG_FILE_EXTENSION = ".log"
ANDROID_TOP_DATASET = [
    LogParserClass("Top_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("Mem:\s*\d+. total,", " ", -2, "Total Mem", False),
    LogParserClass("Mem:\s*\d+. total,\s*\d+. used,", " ", -2,
                   "Used Memory (K)", False),
    LogParserClass("Mem:\s*\d+. total,\s*\d+. used,\s*\d+. free,", " ", -2,
                   "Free Memory (K)", False),
    LogParserClass(
        "Mem:\s*\d+. total,\s*\d+. used,\s*\d+. free,\s*\d+. buffers", " ", -2,
        "Buffer Mem", False),
    LogParserClass("\d+%cpu", "%", 0, "Total CPU %", False),
    LogParserClass("\d+%idle", "%", 0, "Idle CPU %", False),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\stop\s-b", None, [-2, -5], "pkg",
                   False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\stop\s-n", None, [-1, -5], "pkg",
                   False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\sio.appium.settings", None,
                   [-1, -4], "pkg", False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\sio.appium.uiautomator", None,
                   [-1, -4], "pkg", False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\sapp_process\s\Ssystem\Sbin",
                   None, [-1, -5], "pkg", False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\sprocrank", None, [-1, -4],
                   "pkg", False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9}\sdumpsys\smeminfo", None,
                   [-1, -5], "pkg", False, True),
    LogParserClass("^\s+\d+\s\S+\s+(\s*\S+){9} adbd", None, [-1, -4], "pkg",
                   False, True)
]

MEMINFO_LOG_FILE_CONTAINS = "meminfo"
ANDROID_MEMINFO_DATASET = [
    LogParserClass("Meminfo_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("\sUsed\sRAM:\s\S+", ":", 1, "2.Used RAM", False),
    LogParserClass("\s+\d+\S\d+K:\sStack", ":", 0, "3.Stack", False),
    LogParserClass("Total\sRAM:\s\d+,\d+,\d+K", ":", 1, "4.Total", False),
    LogParserClass("^\s+\d+\S+:\s\S+", ":", [1, 0], "pkg:", False, True)
]

PROCRANK_LOG_FILE_CONTAINS = "procrank"
PROCRANK_DATASET = [
    LogParserClass("Procrank_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("\d+(\s+\d+K){8}\s+\S+$", None, [-1, -7], "PSS : ", False,
                   True),
    # LogParserClass("\d+(\s+\d+K){8}\s+\S+$", None, [-1, -8], "RSS : ", False, True),
    # LogParserClass("\d+(\s+\d+K){8}\s+\S+$", None, [-1, -9], "VSS : ", False, True),
    # LogParserClass("\d+(\s+\d+K){8}\s+\S+$", None, [-1, -6], "USS :", False, True)
]

Free_LOG_FILE_CONTAINS = "free"
FREE_H_DATASET = [
    LogParserClass("Free_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("Mem:\s+\S+\s+\S+\s+\S+", None, 1, "2.Mem Total", False),
    LogParserClass("Mem:\s+\S+\s+\S+\s+\S+", None, 2, "3.Mem used", False),
    LogParserClass("Mem:\s+\S+\s+\S+\s+\S+", None, 3, "4.Mem Free", False),
    LogParserClass("Swap:\s+\S+\s+\S+\s+\S+", None, 1, "5.Swap Total", False),
    LogParserClass("Swap:\s+\S+\s+\S+\s+\S+", None, 2, "6.Swap used", False),
    LogParserClass("Swap:\s+\S+\s+\S+\s+\S+", None, 3, "7.Swap Free", False),
]

UFS_LOG_FILE_CONTAINS = "ufs"
UFS_DATASET_1 = [
    LogParserClass("Ufs_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 1], "K size",
                   False, True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 2], "Used:",
                   False, True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 3],
                   "Available:", False, True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 4],
                   "Used in %:", False, True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 5],
                   "Mounted on:", False, True),
]
UFS_DATASET_2 = [
    LogParserClass("Ufs_Cmd_Time: \d+:\d+:\d+", " ", 1, "1.Time", True),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, 0, "Packages",
                   False),
    LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, 2, "Used", False),
    # LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 1], "K size", False, True),
    # LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 2], "Used:", False, True),
    # LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 3], "Available:", False, True),
    # LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 4], "Used in %:", False, True),
    # LogParserClass("\S+\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+", None, [0, 5], "Mounted on:", False, True),
]


class ParseAndroidMemory:
    """ This class is used for Parse Android Memory Logs into the graph and excel file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.common_keywords = CommonKeywordsClass()
        self.config_manager = ConfigurationManager()
        self.path = self.common_keywords.performance_utilization_custom_path(
            MEMORY, ANDROID_MEMORY)
        self.extract_log_class = ExtractPerformanceLogs()

    def parse_android_top_command_logs(self):
        """
        This method is used to parse the android top command data and generate the execl and graph for top.
        :return: None
        """
        try:
            top_df = self.extract_log_class.extract_logs_from_path(self.path,
                                                                   LOG_FILE_CONTAINS,
                                                                   LOG_FILE_EXTENSION,
                                                                   ANDROID_TOP_DATASET,
                                                                   False)
            for sheet_name in top_df:
                top_df[sheet_name].fillna(0)
                top_df[sheet_name]["Total_Command_Packages"] = top_df[
                    sheet_name].filter(like="pkg--").astype(float).sum(axis=1)
                top_df[sheet_name]['Idle CPU %'] = top_df[sheet_name][
                                                       'Idle CPU %'].astype(
                    float) + top_df[sheet_name][
                                                       'Total_Command_Packages'].astype(
                    float)
                # top_df[sheet_name]['CPU Utilization %'] = top_df[sheet_name]['Total CPU %'].astype(float) - top_df[sheet_name]['Idle CPU %'].astype(float)
                top_df[sheet_name][
                    top_df[sheet_name]['Idle CPU %'].astype(float) < 0] = 0
                top_df[sheet_name]["Final Idle CPU %"] = (top_df[sheet_name][
                                                              'Idle CPU %'].astype(
                    float) / 500) * 100
                top_df[sheet_name]['CPU Utilization %'] = 100 - \
                                                          top_df[sheet_name][
                                                              "Final Idle CPU %"].astype(
                                                              float)
                robot_print_debug(
                    f"Avg of Final Idle CPU % {top_df[sheet_name]['Final Idle CPU %']}")
                top_df[sheet_name] = top_df[sheet_name].reindex(
                    sorted(top_df[sheet_name].columns), axis=1)
                self.__plot_android_memory_cpu_top_log(top_df[sheet_name],
                                                       "Android_Top_Data",
                                                       sheet_name)
            self.extract_log_class.save_df_into_execl(top_df,
                                                      "Android_Top_Data",
                                                      ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error(
                f"Error to parse the top command data, EXCEPTION: {exp}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    def parse_adb_mem_pkg_logs(self):
        """
        This method parse the memory logs which is taken by `AndroidMemory.get_android_mem_data(test_case_name: str)`
        method. This create on DataFrame and save this into excel file.
        :except Generic Exception.
        :return: None
        """
        try:
            meminfo_df = self.extract_log_class.extract_logs_from_path(
                self.path, MEMINFO_LOG_FILE_CONTAINS,
                LOG_FILE_EXTENSION,
                ANDROID_MEMINFO_DATASET, False)
            for file in meminfo_df:
                meminfo_df[file] = meminfo_df[file].fillna(0)
                meminfo_df[file]["5.android_stack_usage"] = (meminfo_df[file][
                                                                 "3.Stack"].astype(
                    float) / meminfo_df[file]["4.Total"].astype(float)) * 100
                meminfo_df[file]["5.android_stack_usage"] = meminfo_df[file][
                    "5.android_stack_usage"].apply(lambda x: round(x, 2))
                self.__plot_android_meminfo_package_wise_graph(meminfo_df[file],
                                                               "Android_mem_Data",
                                                               file)
            self.extract_log_class.save_df_into_execl(meminfo_df,
                                                      "Android_mem_Data",
                                                      ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error(
                "Can't parse android memory logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def parse_pro_crank_commands_logs(self):
        """
        This method parse the memory logs which is taken by `AndroidMemory.get_procrank_data(test_case_name: str)`
        method. This create on DataFrame and save this into excel file.
        :return: None
        """
        try:
            procrank_df = self.extract_log_class.extract_logs_from_path(
                self.path, PROCRANK_LOG_FILE_CONTAINS,
                LOG_FILE_EXTENSION,
                PROCRANK_DATASET, False)
            for file in procrank_df:
                procrank_df[file] = procrank_df[file].fillna(0)
                self.__plot_android_procrank_package_wise_graph(
                    procrank_df[file], "Android_procrank_Data", file)
            self.extract_log_class.save_df_into_execl(procrank_df,
                                                      "Android_procrank_Data",
                                                      ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error(
                "Can't parse android procrank logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def parse_android_free_command_logs(self):
        """
        This method is used to parse the android free command data and generate the execl and graph for free.
        :return: None
        """
        try:
            free_df = self.extract_log_class.extract_logs_from_path(self.path,
                                                                    Free_LOG_FILE_CONTAINS,
                                                                    LOG_FILE_EXTENSION,
                                                                    FREE_H_DATASET,
                                                                    False)
            for file in free_df:
                free_df[file] = free_df[file].fillna(0)
                free_df[file]["Android_RAM_Usage"] = free_df[file][
                                                         "3.Mem used"].astype(
                    float) / free_df[file]["2.Mem Total"].astype(float) * 100
                free_df[file]["Android_RAM_Usage"] = free_df[file][
                    "Android_RAM_Usage"].apply(lambda x: round(x, 2))
                self.__plot_android_free_memory_log(free_df[file],
                                                    "Android_free_Data", file)
            self.extract_log_class.save_df_into_execl(free_df,
                                                      "Android_Free_Data",
                                                      ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error(
                "Can't parse android memory logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def parse_ufs_commands_logs(self):
        """
        This method is used to parse the android ufs command data and generate the execl and graph for ufs.
        :return: None
        """
        try:
            ufs_df = self.extract_log_class.extract_logs_from_path(self.path,
                                                                   UFS_LOG_FILE_CONTAINS,
                                                                   LOG_FILE_EXTENSION,
                                                                   UFS_DATASET_1,
                                                                   False)
            for file in ufs_df:
                ufs_df[file].fillna(0)
            self.extract_log_class.save_df_into_execl(ufs_df,
                                                      "Android_Ufs_Data",
                                                      ANDROID_MEMORY)
        except Exception as exp:
            robot_print_error(
                "Can't parse android ufs logs.\nEXCEPTION: %s" % exp)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_error(f"{exc_type, file_name, exc_tb.tb_lineno}")

    def __plot_android_meminfo_package_wise_graph(self, df: pd.DataFrame,
                                                  suite: str,
                                                  title: str = None):
        """
        This method is used to create the graph of meminfo command.
        :param df: dataframe value
        :param suite: Name of the graph which need to be set
        :param title : title of the graph
        """
        try:
            import plotly.graph_objects as go
            packages_names = [pkg_name for pkg_name in df.columns if
                              "pkg:" in pkg_name]
            robot_print_debug(f"Creating graph for packages: {packages_names}")
            df[packages_names] = df[packages_names].astype(float)
            meminfo_table = pd.pivot_table(df, values=packages_names,
                                           index="1.Time")
            data = []
            p = None
            for i in packages_names:
                robot_print_debug(f"Ploting for package: {i}")
                if i == "1.Time":
                    p = go.Scatter(x=meminfo_table.index,
                                   y=meminfo_table[i].astype(int), mode="lines",
                                   name=i)
                else:
                    p = go.Scatter(x=meminfo_table.index, y=meminfo_table[i],
                                   mode="lines", name=i,
                                   visible="legendonly")
                data.append(p)
            fig = go.Figure(data)
            title = title if title is not None else "Android Mem"
            fig.update_layout(title_text=f"Meminfo: {title}",
                              title_font_size=30,
                              xaxis_title="<b>Time<b>",
                              yaxis_title="<b>Total PSS By Category (k) <b>"
                              )
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for meminfo package wise data, EXCEPTION: {exp}",
                print_in_report=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(
                f"Error at: {exc_type, file_name, exc_tb.tb_lineno}")

    def __plot_android_procrank_package_wise_graph(self, df: pd.DataFrame,
                                                   suite: str,
                                                   title: str = None):
        """
        This method is used to create the graph of Procrank command.
        : param suite: Name of the graph which need to be set
        : param df : Dataframe for plotting
        : param title : title of the graph
        """
        try:
            import plotly.graph_objects as go
            packages_names = [pkg_name for pkg_name in df.columns if
                              "PSS : " in pkg_name]
            robot_print_debug(f"Creating graph for packages: {packages_names}")
            df[packages_names] = df[packages_names].astype(float)
            procrank_table = pd.pivot_table(df, values=packages_names,
                                            index="1.Time")
            data = []
            p = None
            for i in packages_names:
                robot_print_debug(f"Ploting for package: {i}")
                if i == "PSS : .qtidataservices":
                    p = go.Scatter(x=procrank_table.index,
                                   y=procrank_table[i].astype(int),
                                   mode="lines", name=i)
                else:
                    p = go.Scatter(x=procrank_table.index, y=procrank_table[i],
                                   mode="lines", name=i,
                                   visible="legendonly")
                data.append(p)
            fig = go.Figure(data)
            title = title if title is not None else "Android Procrank Data"
            fig.update_layout(
                title_text=f"Procrank: {title}",
                title_font_size=30,
                height=800,
                showlegend=True,
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Values<b>",
                yaxis_tickformat="KB",
            )
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for procrank package wise data, EXCEPTION: {exp}",
                print_in_report=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(
                f"Error at: {exc_type, file_name, exc_tb.tb_lineno}")

    def __plot_android_memory_cpu_top_log(self, df: pd.DataFrame, suite: str,
                                          title: str = None):
        """
        This method is used to create the graph of cpu top command.
        : param suite: Name of the graph which need to be set
        : param df : Dataframe for plotting
        : param title : title of the graph
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            fig = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                specs=[[{"type": "scatter"}]]
            )
            title = title if title is not None else "Android CPU"
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>Android CPU Utilisation<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Values(in %)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat="KB",
                hovermode='x unified'
            )
            fig1 = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                specs=[[{"type": "scatter"}]]
            )
            fig1.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>Memory Utilisation<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Values(KB)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat="KB",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["CPU Utilization %"],
                               mode="lines",
                               name="CPU Utilization (%)")
            fig.add_trace(trace, row=1, col=1)
            trace1 = go.Scatter(x=df["1.Time"], y=df["Used Memory (K)"],
                                mode="lines", name="Used Memory (K)")
            trace2 = go.Scatter(x=df["1.Time"], y=df["Free Memory (K)"],
                                mode="lines", name="Free Memory (K)")
            fig1.add_trace(trace1, row=1, col=1)
            fig1.add_trace(trace2, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for Android CPU & MEM, EXCEPTION: {exp}")

    def __plot_android_free_memory_log(self, df: pd.DataFrame, suite: str,
                                       title: str = None):
        """
        This method is used to create the graph of free command.
        : param suite: Name of the graph which need to be set
        : param df : Dataframe for plotting
        : param title : title of the graph
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            fig = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                specs=[[{"type": "scatter"}]]
            )
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>Free -h Memory Utilisation {title}<b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Values(MB)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat="MB",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["Android_RAM_Usage"],
                               mode="lines",
                               name="Android_RAM_Usage (%)")
            fig.add_trace(trace, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for Android Free, EXCEPTION: {exp}")

# todo: below code for future use, as per latest changes its not done
# def parse_adb_procstats_logs(self, package_list: List = None):
#     """
#     This method is used to parse the procstats data of android memory info.
#     User need to pass the package list if he want to parse particular packages.
#     It will take the package list in two way:
#         1. By using argument "package_list" which is the first priority.
#         2. If user not pass the argument then method will check the config file and try to get
#             the package list.
#         3. If not package list is provided by the user either config file or as an argument then it will only
#             capture the total of all the process.
#     :param package_list: List of the package which data need to be capture and shown in graph
#     :type package_list: List
#     :return: None
#     :rtype: None
#     """
#     try:
#         df = pd.DataFrame()
#         list_of_packages = []
#         # check that user provide the package list
#         if package_list is not None:
#             list_of_packages = package_list
#         else:
#             # if user not provided check from config file
#             list_of_packages = self.config_manager.get_android_mem_packages()
#         # if method not get the package list Just notify the user.
#         if len(list_of_packages) == 0:
#             robot_print_warning(f"Not package list provided by the user, "
#                                 f"We are not able to parse the logs package wise."
#                                 f" But your logs are saved inside report.", print_in_report=True)
#         row = 0
#         fp = None
#         path = self.common_keywords.performance_utilization_custom_path(MEMORY, ANDROID_MEMORY)
#         # getting all the file form the report and parsing one by one
#         log_list = os.listdir(path=path)
#         if log_list:
#             for log_file in progressBar(log_list, prefix='Progress:', suffix='Complete', length=len(log_list)):
#                 file_path = os.path.join(path, log_file)
#                 with open(file_path, "r") as fp:
#                     line = fp.readline()
#                     while line:
#                         if "TIME:" in line:
#                             time = line.split(" ")[1].strip()
#                             row = row + 1
#                             df.loc[row, "Usecase"] = log_file.replace(".log", "")
#                             df.loc[row, "Time"] = datetime.strptime(time, "%H:%M:%S").time()
#                         if "com." in line:
#                             for package in list_of_packages:
#                                 try:
#                                     if package in line.strip().split("/")[0]:
#                                         line = fp.readline()
#                                         pss = line.strip().split(" ")[2].split("/")[0].replace("(", "").split("-")
#                                         if len(pss) == 3:
#                                             df.loc[row, f"{package}(In MB)"] = float(pss[-1].replace("MB", ""))
#                                 except Exception as exp:
#                                     robot_print_error(f"Error to get the package info from procstats logs, "
#                                                       f"EXCEPTION: {exp}", print_in_report=True)
#                         if "TOTAL" in line:
#                             match = re.search("TOTAL\s*:\s*(\d+.\d+)", line.strip())
#                             if match:
#                                 df.loc[row, "Total(in GB)"] = float(match[0].split(":")[1].strip())
#                         line = fp.readline()
#                     fp.close()
#                 self.__save_parse_data(df=df, sheet_name="Procstats")
#     except Exception as exp:
#         robot_print_error(f"Error to parse the adb procstats data, EXCEPTION: {exp}\n"
#                           f"Logs will be save inside the report.", print_in_report=True)
#
#     finally:
#         ParseAndroidMemory.__excel_file = None
#
