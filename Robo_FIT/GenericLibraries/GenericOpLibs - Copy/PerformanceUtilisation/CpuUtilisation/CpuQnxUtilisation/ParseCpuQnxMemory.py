""" All Lib file import which is required for this file"""
import re

from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.ExtractPerformanceLogs import \
    ExtractPerformanceLogs
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.LogParsing.LogParserClass import \
    LogParserClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_error
import pandas as pd
import os
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import \
    CPU, QNX_CPU
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import \
    ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import \
    CommonKeywordsClass

"""Below dataset used for parse the QNX top log with help of Regular Expression"""

LOG_FILE_CONTAINS = "qnx"
LOG_FILE_EXTENSION = ".log"
QNX_TOP_DATASET = [
    LogParserClass("Date: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1, "1.Time",
                   True, False),
    LogParserClass("(\d+\s+\d+\s\S+\s+\S+\s+\S+\s)(?!qvm)(\S+)", None,
                   [[-1, 0], -2], "pkg ", False, True)
]


class ParseCpuQnxMemory:
    """ This class is used for Parse CPU QNX Memory Logs into the graph and excel"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.common_keywords = CommonKeywordsClass()
        self.config_manager = ConfigurationManager()
        self.path = self.common_keywords.performance_utilization_custom_path(
            CPU, QNX_CPU)
        self.serial_log_path = os.path.join(
            self.common_keywords.get_report_path(), "Serial_Logs")
        self.extract_log_class = ExtractPerformanceLogs()

    def parse_qnx_cpu_top_data(self):
        """
        This method parse the memory logs which is taken by `capture_top_logs()`
        method. This create on DataFrame and save this into excel file.
        :except Generic Exception.
        :return: None
        """
        cpu_top_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path, LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_TOP_DATASET, False)
        for file in cpu_top_df:
            cpu_top_df[file] = cpu_top_df[file].fillna(0)
            for log_parser_set in QNX_TOP_DATASET:
                if log_parser_set.IS_DYNAMIC:
                    search_filter = log_parser_set.COL_NAME
                    columns_filters_to_sum = []
                    for column_name in cpu_top_df[file].columns:
                        if search_filter in column_name:
                            column_filter = "--".join(
                                column_name.split("--")[0:-1])
                            if column_filter not in columns_filters_to_sum:
                                columns_filters_to_sum.append(column_filter)
                    robot_print_debug(
                        f"columns_filters_to_sum = {columns_filters_to_sum}")
                    for column_filter in columns_filters_to_sum:
                        total_col_name = "Total_" + column_filter
                        cpu_top_df[file][total_col_name] = cpu_top_df[
                            file].filter(like=f"{column_filter}").astype(
                            float).sum(axis=1)
            self.__plot_qnx_memory_top_log(cpu_top_df[file])
            new_column_names = {col: re.sub(r'[^\w\s]', '_', col) for col in
                                cpu_top_df[file].columns}
            cpu_top_df[file].rename(columns=new_column_names, inplace=True)
        self.extract_log_class.save_df_into_execl(cpu_top_df,
                                                  f"QNX_CPU_Top_Data", QNX_CPU,
                                                  CPU)

    def __plot_qnx_memory_top_log(self, df: pd.DataFrame):
        """
        This method is used to create the graph of top command.
        :param df: df which we want graph
        :return: None
        """
        try:
            import plotly.graph_objects as go
            cpu_names = [pkg_name for pkg_name in df.columns if
                         "Total_" in pkg_name]
            robot_print_debug(f"Creating graph for packages: {cpu_names}")
            df[cpu_names] = df[cpu_names].astype(float)
            top_table = pd.pivot_table(df, values=cpu_names, index="1.Time")
            data = []
            p = None
            for i in cpu_names:
                robot_print_debug(f"Ploting for package: {i}")
                if i in "":
                    p = go.Scatter(x=top_table.index, y=top_table[i],
                                   mode="lines", name=i)
                else:
                    p = go.Scatter(x=top_table.index, y=top_table[i],
                                   mode="lines", name=i,
                                   visible="legendonly")
                data.append(p)
            fig = go.Figure(data)
            fig.update_layout(title_text="Qnx CPU Pkg Wise Utilization",
                              title_font_size=30,
                              xaxis_title="<b>Time<b>",
                              yaxis_title="<b>Total Packages SUM in % <b>", )
            with open(os.path.join(self.path, f"QNX_CPU_TOP_Data.html"),
                      'w') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for QNX CPU, EXCEPTION: {exp}")
