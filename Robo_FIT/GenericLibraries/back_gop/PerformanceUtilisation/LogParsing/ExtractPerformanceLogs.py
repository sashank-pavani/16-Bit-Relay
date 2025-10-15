import os
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import \
    CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import \
    robot_print_error, robot_print_debug, \
    robot_print_info
import pandas as pd
from robot.api import logger

RE_MATCH_INDEX = 0
COMBINED_SHEET_NAME = "Memory"


def progressBar(iterable, prefix='', suffix='', decimals=1, length=100,
                fill='█',
                print_end="\r"):
    """
    This Method is used to Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        logger.console(f'\r{prefix} |{bar}| {percent}% {suffix}' + print_end,
                       newline=False)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    robot_print_debug("Complete Parsing")


class ExtractPerformanceLogs:
    """
    This Class is used to extract the logs from file and save that into one df
    """
    __excel_file = None

    def __init__(self):
        """
        This init used for initialize other classes
        """
        self.common_keywords = CommonKeywordsClass()

    def __extract_logs_from_file(self, i_in_file_path, i_log_parsers_datasets,
                                 i_df, i_df_row):
        """
        This function is used for extract the logs from log file with the help of parser dataset
        and stores/returns it using argument pd.df, input i_df can also have previous data
        in that case new data is appended to it after given row count (i_df_row)
        :param i_in_file_path : file path where log file is present
        :param i_log_parsers_datasets : dataset (list) which contain the RE expression with column
        :param i_df : df to store the parsed information, as mentioned in description
            this can be empty df with (i_df_row=0) or can have previous data
        :param i_df_row : row count after which new data to be appended to i_df
        :return : df and df row num
        """
        robot_print_info(
            f"[ extract_logs_from_file ]: Extracting data from file {i_in_file_path}")
        robot_print_debug(
            "[ extract_logs_from_file ]: with i_log_parserS_DATASET = \n" + "\n".join(
                [str(dataset) for dataset in i_log_parsers_datasets]))
        with open(i_in_file_path) as in_file:
            for line in in_file.readlines():
                for log_parser in i_log_parsers_datasets:
                    match_re = log_parser.search_re.search(line)
                    if match_re:
                        robot_print_debug(
                            f"Match is found for {log_parser.SEARCH_PATTERN} : {match_re[RE_MATCH_INDEX]}")
                        match_re_parts = match_re[RE_MATCH_INDEX].split(
                            log_parser.DATA_SEPERATOR)
                        if log_parser.INCREASE_ROW:
                            i_df_row += 1
                        col_name = log_parser.COL_NAME
                        if log_parser.IS_DYNAMIC:
                            # col_name = log_parser.COL_NAME + match_re_parts[(log_parser.DATA_INDEX[0])].strip()
                            if type(log_parser.DATA_INDEX[0]) == list:
                                for index in log_parser.DATA_INDEX[0]:
                                    col_name += '--' + match_re_parts[
                                        index].strip()
                            else:
                                col_name += '--' + match_re_parts[
                                    (log_parser.DATA_INDEX[0])].strip()
                            i_df.loc[i_df_row, col_name] = match_re_parts[
                                (log_parser.DATA_INDEX[1])].replace('%',
                                                                    '').replace(
                                'M', '').replace('K', '').replace('G',
                                                                  '').replace(
                                ',', '').replace('(bytes)', '').replace('[',
                                                                        '').replace(
                                '=', '').replace('/', '').strip()
                        else:
                            i_df.loc[i_df_row, col_name] = match_re_parts[
                                log_parser.DATA_INDEX].replace('%', '').replace(
                                'M', '').replace('K', '').replace('G',
                                                                  '').replace(
                                ',', '').replace('=', '').replace('[',
                                                                  '_').replace(
                                '/', '').strip()
        i_df = i_df.reindex(sorted(i_df.columns), axis=1)
        robot_print_debug(
            f"[ extract_logs_from_file ]: Extracted df = \n{i_df}")
        return i_df, i_df_row

    def extract_logs_from_path(self, i_in_file_path, i_log_file_contains,
                               i_log_file_extension, i_log_parser_dataset,
                               flag_combine_df=True):
        """
        This function is used to extract logs from path and return the dict df
        :param i_in_file_path: file path that you want to extract
        :param i_log_file_extension: Extension of file (eg .log)
        :param i_log_parser_dataset: Parser dataset is Logparser class object
        :param flag_combine_df: 0 or row num for if we want data in only  one excel
        :param i_log_file_contains: Uinque string which can find which log type(eg , strings top,meminfo)
        """
        list_of_log_files = os.listdir(i_in_file_path)
        robot_print_debug("[extract_logs_from_path] : List of files: " + str(
            list_of_log_files))
        dict_df = {}
        combined_df = pd.DataFrame()
        combined_df_row = 0
        for in_file_name in progressBar(list_of_log_files, prefix='Progress:',
                                        suffix='Complete',
                                        length=len(list_of_log_files)):
            if i_log_file_contains in in_file_name and in_file_name.endswith(
                    i_log_file_extension):
                file_path = os.path.join(i_in_file_path, in_file_name)
                if flag_combine_df:
                    (
                        combined_df,
                        combined_df_row) = self.__extract_logs_from_file(
                        file_path, i_log_parser_dataset,
                        combined_df, combined_df_row)
                else:
                    (temp_df, temp_df_row) = self.__extract_logs_from_file(
                        file_path, i_log_parser_dataset,
                        pd.DataFrame(),
                        0)  # passing new df with initial index 0
                    dict_df[in_file_name] = temp_df
        if flag_combine_df:
            dict_df[COMBINED_SHEET_NAME] = combined_df
        robot_print_info(
            f"[ extract_logs_from_path ]: Extracted df = \n{dict_df}")
        return dict_df

    def save_df_into_execl(self, i_dict_df, i_out_file_name, sub_folder,
                           folder_name="Memory"):
        """
        This Function is used to save df values into excel
        :param i_dict_df : dict of df or single df
        :param i_out_file_name: xlsx name of file which you want to save
        :param sub_folder: Performance Utilization sub folder name like AndroidMemory or QnxMemory
        :param folder_name: "Memory" or "CPU" Main folders of Performance Utilization, default is Memory
        """
        path = os.path.join(
            self.common_keywords.performance_utilization_custom_path(
                folder_name, sub_folder), f"{i_out_file_name}.xlsx")
        robot_print_info(f"path is {path}")
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for i_sheet_name in i_dict_df:
                i_dict_df[i_sheet_name].to_excel(writer,
                                                 sheet_name=i_sheet_name[0:31])
