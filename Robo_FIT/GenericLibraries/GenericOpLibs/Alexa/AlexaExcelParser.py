import pandas as pd

from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_debug
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ExcelParser import ExcelParser
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.Constants import ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME


class AlexaExcelParser:
    """
           This class is responsible for handling Alexa  excel operations.
       """

    def __init__(self, alexa_excel_name, feature_parent_folder):
        """
             Constructor of AlexaExcelParser
        """
        try:
            self.common_keywords = CommonKeywordsClass()
            self.excel_parser = ExcelParser(ALEXA_EXCEL_NAME, PARENT_FOLDER_NAME)
            self.alexa_excel_name = alexa_excel_name
            self.feature_parent_folder = feature_parent_folder
            self.input_file_path = self.common_keywords.get_path(alexa_excel_name, feature_parent_folder, is_file=True,
                                                                 is_dir=False)
            self.df = pd.read_excel(self.input_file_path)

        except FileNotFoundError as file_exp:
            robot_print_error(f"{self.excel_parser} or {self.alexa_excel_name} not found, Please create first and then "
                              f"try to Access this Library. EXCEPTION : {file_exp}")
        except IOError as io_error:
            robot_print_error(f"There is an exception to read the input excel file!!, "
                              f"Exception: {io_error}")
        except Exception as exp:
            robot_print_error(f"Error in Alexa Excel parser Class Constructor EXCEPTION:{exp}")

    def _get_input_cell_excel_data(self, unique_key) -> str:
        """
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        :return: corresponding value for the key
        """
        try:
            status = self.excel_parser.get_cell_value(unique_key, unique_key_column_name="ID",
                                                      get_value_from_column="Input command")
            return status
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def _get_output_cell_excel_data(self, unique_key):
        """
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        :return: corresponding value for the key
        """
        try:
            status = self.excel_parser.get_cell_value(unique_key, unique_key_column_name="ID",
                                                      get_value_from_column="Actual Output")
            return status
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def _get_expected_cell_excel_data(self, unique_key) -> any:
        """
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        :return: corresponding value for the key
        """
        try:
            status = self.excel_parser.get_cell_value(unique_key, unique_key_column_name="ID",
                                                      get_value_from_column="Expected Output")
            return status
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def _write_actual_output_to_cell_data(self, unique_key, value_to_set) -> str:
        """
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        :param value_to_set: new cell value to be set in the cell
        """
        try:
            self.excel_parser.write_to_cell(unique_key, "ID", value_to_set,
                                            write_to_column="Actual Output")
            return value_to_set
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def _write_status_to_cell_data(self, unique_key, value_to_set):
        """
        :param unique_key:element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        :param value_to_set: new cell value to be set in the cell
        """
        try:
            self.excel_parser.write_to_cell(unique_key, "ID", value_to_set, write_to_column="Status")
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def delete_the_values_from_column(self, column_name: str):
        """
        It will delete the values from column
        :param column_name: name of the column which need to be deleted
        """
        try:
            self.df[column_name] = None
            writer = pd.ExcelWriter(self.input_file_path)
            self.df.to_excel(writer, index=False)
            writer.save()
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def compare_cell_values(self, unique_key: str):
        """
        The method will be used for comparing the cell values
        :param unique_key: name of the module in which all the folder is created
        :return:bool
        """
        try:
            status = self.excel_parser.compare_cell_values(unique_key, "ID", "Actual Output", "Expected Output")
            robot_print_debug(f"status is:", status)
            return status
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")
