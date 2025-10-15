""" All Lib file import which is required for this file"""
from plotly.subplots import make_subplots
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
import sys
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.CommanVariables import \
    MEMORY, QNX_MEMORY
from Robo_FIT.GenericLibraries.GenericOpLibs.PerformanceUtilisation.ConfigurationManager import \
    ConfigurationManager
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import \
    CommonKeywordsClass

"""Below datasets used for parse the top/showmem/slog2info/pmem/DMA log with help of Regular Expression"""

LOG_FILE_CONTAINS = "qnx"
LOG_FILE_EXTENSION = ".log"
QNX_TOP_DATASET = [
    LogParserClass("Date: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1, "1.Time",
                   True, False),
    LogParserClass("CPU  \d Idle: \d+.\d+%", "Idle:", [0, 1], "idle_", False,
                   True),
    LogParserClass("Memory:\s*\d+. total,", " ", -2, "2.Total Memory"),
    LogParserClass("Memory:\s*\d+. total,\s*\d+. avail,", " ", -2,
                   "3.Available Memory"),
    LogParserClass("CPU states:\s*\d+.\d% user,", " ", -2, "4.CPU_user_values"),
    LogParserClass("CPU states:\s*\d+.\d% user,\s\d+.\d+%\skernel", " ", -2,
                   "5.CPU_kernel_values"),
    LogParserClass("\s\d\s+\d+\s\S+\s+\S+\s+\S+\sqvm", None, [0, -2], "qvm_",
                   False, True)
]

QNX_SHOWMEM_A_DATASET = [
    LogParserClass("showmem_a: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1,
                   "1.Time", True),
    LogParserClass("Total process memory in use\s:\s\d+", ":", -1,
                   "2.Total Mem"),
    LogParserClass("^\s+\S+ [|]\s+\S+ [|]\s+\S+ [|]\s+\d+\S* [|]", "|", [0, 3],
                   "pkg: ", False, True),
    LogParserClass("^\s+\S+ [|]\s+\S+ [|]\s+\S+ [|]\s+\S+ [|]\s+\d+\S* [|]",
                   "|", [0, 4], "stack_pkg: ", False, True)
]

QNX_SHOWMEM_S_DATASET = [
    LogParserClass("showmem_s: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1,
                   "1.Time", True),
    LogParserClass("sysram\s+\d+\s+\d+\s+\d+", None, 1, "3.Total", False),
    LogParserClass("sysram\s+\d+\s+\d+\s+\d+", None, 2, "2.Used", False),
    LogParserClass("sysram\s+\d+\s+\d+\s+\d+", None, 3, "4.Free", False),
]

QNX_Pmem_DATASET = [
    LogParserClass("showmem_s: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1,
                   "1.Time", True),
    LogParserClass("gvm_pmem\s+\d+\s+\d+\s+\d+", None, 1, "PMEM_Total", False),
    LogParserClass("gvm_pmem\s+\d+\s+\d+\s+\d+", None, 2, "PMEM_Used", False),
    LogParserClass("gvm_pmem\s+\d+\s+\d+\s+\d+", None, 3, "PMEM_Free", False),
]
QNX_Dmem_DATASET = [
    LogParserClass("showmem_s: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1,
                   "1.Time", True),
    LogParserClass("mm_dma\s+\d+\s+\d+\s+\d+", None, 1, "MM_DMA_Total", False),
    LogParserClass("mm_dma\s+\d+\s+\d+\s+\d+", None, 2, "MM_DMA_Used", False),
    LogParserClass("mm_dma\s+\d+\s+\d+\s+\d+", None, 3, "MM_DMA_Free", False),
]
QNX_UFS_DATASET = [
    LogParserClass("ufs: \d+-\d+-\d+ Time: \d+:\d+:\d+", " ", -1, "1.Time",
                   True),
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


class ParseQnxMemory:
    """ This class is used for Parse QNX Memory Logs into the Graph and excel file"""

    def __init__(self):
        """
        This init used for initialize other classes and config file
        """
        self.common_keywords = CommonKeywordsClass()
        self.config_manager = ConfigurationManager()
        self.path = self.common_keywords.performance_utilization_custom_path(
            MEMORY, QNX_MEMORY)
        self.serial_log_path = os.path.join(
            self.common_keywords.get_report_path(), "Serial_Logs")
        self.extract_log_class = ExtractPerformanceLogs()

    def parse_qnx_showmem_log(self):
        """
        This method parse the memory logs which is taken by `capture_qnx_showmem_logs()`
        method. This create on DataFrame and save this into excel file.
        :except Generic Exception.
        :return: None
        """
        shoemem_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path,
            LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_SHOWMEM_A_DATASET,
            False)
        for file in shoemem_df:
            shoemem_df[file] = shoemem_df[file].fillna(0)
            shoemem_df[file]["Total_Mem"] = shoemem_df[file].filter(
                like="pkg:").astype(float).sum(axis=1)
            shoemem_df[file]["stack_Mem"] = shoemem_df[file].filter(
                like="stack_pkg:").astype(float).sum(axis=1)
            shoemem_df[file]["qnx_stack_usage"] = shoemem_df[file][
                                                      "stack_Mem"] / \
                                                  shoemem_df[file][
                                                      "Total_Mem"] * 100
            shoemem_df[file]["qnx_stack_usage"] = shoemem_df[file][
                "qnx_stack_usage"].apply(lambda x: round(x, 2))
            self.__plot_qnx_showmem_a_package_wise_graph(shoemem_df[file])
        self.extract_log_class.save_df_into_execl(shoemem_df,
                                                  "QNX_show_mem_Data",
                                                  QNX_MEMORY)

    def parse_qnx_top_data(self):
        """
        This method parse the memory logs which is taken by `capture_top_logs()`
        method. This create on DataFrame and save this into excel file.
        :except Generic Exception.
        :return: None
        """
        top_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path, LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_TOP_DATASET, False)
        for file in top_df:
            top_df[file] = top_df[file].fillna(0)
            top_df[file]["Total_QVM"] = top_df[file].filter(like="qvm").astype(
                float).sum(axis=1)
            top_df[file]["Total_CPU_Utilisation"] = top_df[file].filter(
                like="idle").astype(float).sum(axis=1)
            top_df[file]["Total_CPU_Utilisation"] = 800 - top_df[file][
                "Total_CPU_Utilisation"].astype(float)
            top_df[file]["Total_CPU_Utilisation"] = top_df[file][
                "Total_CPU_Utilisation"].replace(800, 0)
            top_df[file]["Android_CPU_Utilisation"] = 8 * top_df[file][
                "Total_QVM"].astype(float)
            top_df[file]["QNX_CPU_Utilisation"] = top_df[file][
                                                      "Total_CPU_Utilisation"] - \
                                                  top_df[file][
                                                      "Android_CPU_Utilisation"]
            top_df[file]["QNX_CPU_Usage"] = top_df[file][
                                                "4.CPU_user_values"].astype(
                float) + top_df[file]["5.CPU_kernel_values"].astype(float)
            top_df[file]["Android_CPU_Usage"] = (top_df[file][
                                                     "Android_CPU_Utilisation"] / 500) * 100
            top_df[file]["Android_CPU_Usage"] = top_df[file][
                "Android_CPU_Usage"].apply(lambda x: round(x, 2))
            self.__plot_qnx_memory_top_log(top_df[file])
            self.__plot_qnx_cpu_utilization(top_df[file])
        self.extract_log_class.save_df_into_execl(top_df, f"QNX_Top_Data",
                                                  QNX_MEMORY)

    def parse_qnx_showmem_summary_logs(self):
        """
        This method is used to parse the showmem -s logs.
        :return: None
        :rtype: None
        """
        sum_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path, LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_SHOWMEM_S_DATASET)
        for sheet_name in sum_df:
            sum_df[sheet_name].fillna(0)
            sum_df[sheet_name]['Qnx_RAM_Usage'] = (sum_df[sheet_name][
                                                       '2.Used'].astype(float) /
                                                   sum_df[sheet_name][
                                                       '3.Total'].astype(
                                                       float)) * 100
            sum_df[sheet_name]["Qnx_RAM_Usage"] = sum_df[sheet_name][
                "Qnx_RAM_Usage"].apply(lambda x: round(x, 2))
            sum_df[sheet_name] = sum_df[sheet_name].reindex(
                sorted(sum_df[sheet_name].columns), axis=1)
            self.__plot_qnx_memory_used_log(sum_df[sheet_name],
                                            "QNX_summary_Data", sheet_name)
        self.extract_log_class.save_df_into_execl(sum_df, "QNX_summary_Data",
                                                  QNX_MEMORY)

    def parse_qnx_pmem_logs(self):
        """
        This method is used to parse the Pmem from showmem -s logs.
        :return: None
        :rtype: None
        """
        pmem_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path, LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_Pmem_DATASET)
        for sheet_name in pmem_df:
            pmem_df[sheet_name].fillna(0)
            pmem_df[sheet_name]['Qnx_PMEM_Usage'] = (pmem_df[sheet_name][
                                                         'PMEM_Used'].astype(
                float) /
                                                     pmem_df[sheet_name][
                                                         'PMEM_Total'].astype(
                                                         float)) * 100
            pmem_df[sheet_name]["Qnx_PMEM_Usage"] = pmem_df[sheet_name][
                "Qnx_PMEM_Usage"].apply(lambda x: round(x, 2))
            pmem_df[sheet_name] = pmem_df[sheet_name].reindex(
                sorted(pmem_df[sheet_name].columns), axis=1)
            self.__plot_qnx_pmem_used_log(pmem_df[sheet_name], "QNX_PMEM_Data",
                                          sheet_name)
        self.extract_log_class.save_df_into_execl(pmem_df, "QNX_PMEM_Data",
                                                  QNX_MEMORY)

    def parse_qnx_dmem_logs(self):
        """
        This method is used to parse the dmem logs showmem -s commands.
        :return: None
        :rtype: None
        """
        dmem_df = self.extract_log_class.extract_logs_from_path(
            self.serial_log_path, LOG_FILE_CONTAINS,
            LOG_FILE_EXTENSION,
            QNX_Dmem_DATASET)
        for sheet_name in dmem_df:
            dmem_df[sheet_name].fillna(0)
            dmem_df[sheet_name]['Qnx_DMA_Usage'] = (dmem_df[sheet_name][
                                                        'MM_DMA_Used'].astype(
                float) /
                                                    dmem_df[sheet_name][
                                                        'MM_DMA_Total'].astype(
                                                        float)) * 100
            dmem_df[sheet_name]["Qnx_DMA_Usage"] = dmem_df[sheet_name][
                "Qnx_DMA_Usage"].apply(lambda x: round(x, 2))
            dmem_df[sheet_name] = dmem_df[sheet_name].reindex(
                sorted(dmem_df[sheet_name].columns), axis=1)
            self.__plot_qnx_dmem_used_log(dmem_df[sheet_name], "QNX_DMA_Data",
                                          sheet_name)
        self.extract_log_class.save_df_into_execl(dmem_df, "QNX_DMA_Data",
                                                  QNX_MEMORY)

    def parse_qnx_ufs_data(self):
        """
        This method is used to parse the qnx ufs logs df -k commands.
        :return: None
        :rtype: None
        """
        ufs_df = self.extract_log_class.extract_logs_from_path(self.serial_log_path, LOG_FILE_CONTAINS,
                                                               LOG_FILE_EXTENSION, QNX_UFS_DATASET)
        for sheet_name in ufs_df:
            ufs_df[sheet_name].fillna(0)
            ufs_df[sheet_name] = ufs_df[sheet_name].reindex(sorted(ufs_df[sheet_name].columns), axis=1)
        self.extract_log_class.save_df_into_execl(ufs_df, "QNX_UFS_Data",
                                                  QNX_MEMORY)

    def __plot_qnx_showmem_a_package_wise_graph(self, df: pd.DataFrame):
        """
        This method is used to plot the graph for showmem -a command.
        :param : dataframe for plotting
        :return: None
        """
        try:
            import plotly.graph_objects as go
            fig1 = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                specs=[[{"type": "scatter"}]]
            )
            fig1.layout.update(
                height=800,
                showlegend=True,
                title_text="Qnx showmem -a Graph",
                title_font_size=30,
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Total Process Memory (in Kb)<b>",
                yaxis_tickformat="KB",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["2.Total Mem"],
                               mode="lines",
                               name="Total process memory in use (KB)")
            fig1.add_trace(trace, row=1, col=1)
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
                if i in "Total":
                    p = go.Scatter(x=meminfo_table.index, y=meminfo_table[i],
                                   mode="lines", name=i)
                else:
                    p = go.Scatter(x=meminfo_table.index, y=meminfo_table[i],
                                   mode="lines", name=i,
                                   visible="legendonly")
                data.append(p)
            fig = go.Figure(data)
            fig.update_layout(title_text="Package Wise Memory",
                              xaxis_title="<b>Time<b>",
                              yaxis_title="<b>Total mem (KB)<b>",
                              yaxis_tickformat="KB")
            with open(os.path.join(self.path, f"QNX_Showmem_a_Data.html"),
                      'w') as f:
                f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for meminfo package wise data, EXCEPTION: {exp}",
                print_in_report=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            robot_print_debug(
                f"Error at: {exc_type, file_name, exc_tb.tb_lineno}")

    def __plot_qnx_memory_used_log(self, df: pd.DataFrame, suite: str,
                                   title: str = None):
        """
        This method is used to create the graph of top command.
        :param suite: Name of graph
        :param df: dataframe for plot
        :param title : title of the graph
        :return: None
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
            title = title if title is not None else ""
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>QNX Total Used Memory Utilisation in %<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Total Used Memory(in %)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat="KB",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["Qnx_RAM_Usage"],
                               mode="lines",
                               name="QNX RAM Usage %")
            fig.add_trace(trace, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for Android CPU & MEM, EXCEPTION: {exp}")

    def __plot_qnx_pmem_used_log(self, df: pd.DataFrame, suite: str,
                                 title: str = None):
        """
        This method is used to create the graph of pmem output.
        :param suite: Name of graph
        :param df: dataframe for plot
        :param title : title of the graph
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
            title = title if title is not None else ""
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>QNX PMEM Usage in %<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Total Pmem Used Memory(in %)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat=",.2f",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"],
                               y=df["Qnx_PMEM_Usage"].astype(float),
                               mode="lines",
                               name="QNX PMEM Usage %")
            fig.add_trace(trace, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for PMEM, EXCEPTION: {exp}")

    def __plot_qnx_dmem_used_log(self, df: pd.DataFrame, suite: str,
                                 title: str = None):
        """
        This method is used to create the graph of demem output.
        :param suite: Name of graph
        :param df: dataframe for plot
        :param title : title of the graph
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
            title = title if title is not None else ""
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>QNX MM_DMA Usage in %<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Total MM_DMA Used Memory(in %)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat=",.2f",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["Qnx_DMA_Usage"],
                               mode="lines",
                               name="QNX MM_DMA Usage %")
            fig.add_trace(trace, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for PMEM, EXCEPTION: {exp}")

    def __plot_qnx_slog2_busy_log(self, df: pd.DataFrame, suite: str,
                                  title: str = None):
        """
        This method is used to create the graph of slog2info command.
        :param suite: Name of graph
        :param df: dataframe for plot
        :param title : title of the graph
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
            title = title if title is not None else ""
            fig.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>QNX Slog2 Busy Values in %<i>{title}<i><b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Busy Values(in %)<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat=",.2f",
                hovermode='x unified'
            )
            trace = go.Scatter(x=df["1.Time"], y=df["Busy_in_Percentage"],
                               mode="lines",
                               name="QNX Slog2 Busy in %")
            fig.add_trace(trace, row=1, col=1)
            with open(os.path.join(self.path, f"{suite}.html"), 'a+') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for PMEM, EXCEPTION: {exp}")

    def __plot_qnx_memory_top_log(self, df: pd.DataFrame):
        """
        This method is used to create the graph of top command.
        :param df: dataframe for plot
        """
        try:
            import plotly.graph_objects as go
            cpu_names = [pkg_name for pkg_name in df.columns if
                         "idle_" in pkg_name]
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
            fig.update_layout(title_text="Qnx CPU Idle Values Graph",
                              title_font_size=30,
                              xaxis_title="<b>Time<b>",
                              yaxis_title="<b>CPU idle in % <b>", )
            qvm_names = [pkg_name for pkg_name in df.columns if
                         "qvm" in pkg_name]
            robot_print_debug(f"Creating graph for packages: {qvm_names}")
            df[qvm_names] = df[qvm_names].astype(float)
            top_table = pd.pivot_table(df, values=qvm_names, index="1.Time")
            qvm_data = []
            qvm_p = None
            for i in qvm_names:
                robot_print_debug(f"Ploting for package: {i}")
                if i in "":
                    qvm_p = go.Scatter(x=top_table.index, y=top_table[i],
                                       mode="lines", name=i)
                else:
                    qvm_p = go.Scatter(x=top_table.index, y=top_table[i],
                                       mode="lines", name=i,
                                       visible="legendonly")
                qvm_data.append(qvm_p)
            fig1 = go.Figure(qvm_data)
            fig1.update_layout(title_text="Qnx Qvm Values Graph",
                               title_font_size=30,
                               xaxis_title="<b>Time<b>",
                               yaxis_title="<b>CPU qvm values % <b>", )
            with open(os.path.join(self.path, f"QNX_TOP_Data.html"), 'w') as f:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for QNX CPU, EXCEPTION: {exp}")

    def __plot_qnx_cpu_utilization(self, df: pd.DataFrame):
        """
        This method is used to create the graph of cpu utilization
        :param df : dataframe for plotting
        """
        try:
            import plotly.graph_objects as go
            fig2 = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                specs=[[{"type": "scatter"}]]
            )
            fig2.layout.update(
                height=800,
                showlegend=True,
                title_text=f"<b>System CPU Utilization<b>",
                xaxis_title="<b>Time<b>",
                yaxis_title="<b>Values<b>",
                legend_title="<b>Data<b>",
                yaxis_tickformat="KB",
                hovermode='x unified'
            )
            trace1 = go.Scatter(x=df["1.Time"], y=df["Total_CPU_Utilisation"],
                                mode="lines",
                                name="Total_CPU_Utilisation")
            trace2 = go.Scatter(x=df["1.Time"], y=df["Android_CPU_Utilisation"],
                                mode="lines",
                                name="Android_CPU_Utilisation")
            trace3 = go.Scatter(x=df["1.Time"], y=df["QNX_CPU_Utilisation"],
                                mode="lines", name="QNX_CPU_Utilisation")
            fig2.add_trace(trace1, row=1, col=1)
            fig2.add_trace(trace2, row=1, col=1)
            fig2.add_trace(trace3, row=1, col=1)
            with open(os.path.join(self.path, f"System_CPU_Utilization.html"),
                      'w') as f:
                f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
        except Exception as exp:
            robot_print_error(
                f"Error to plot the graph for QNX CPU Utilisation, EXCEPTION: {exp}")
