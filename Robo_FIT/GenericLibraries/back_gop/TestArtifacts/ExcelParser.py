import os.path
import pandas as pd
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import *
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from typing import List


class ExcelParser:

    def __init__(self, excel_name, parent_folder):
        """
        Constructor of ExcelParser
        :param excel_name: name of the Excel file with extension
        :param parent_folder: folder name in which Excel file will be stored
        """
        try:
            self.excel_parser = ExcelParser
            self.excel_name = excel_name
            self.parent_folder = parent_folder
            self.common_keyword = CommonKeywordsClass()
            self.input_file_path = self.common_keyword.get_path(excel_name, parent_folder, is_file=True,
                                                                is_dir=False)
            self.df = pd.read_excel(self.input_file_path)
        except FileNotFoundError as file_exp:
            robot_print_error(f"{self.excel_name} or {self.parent_folder} not found, Please create first and then "
                              f"try to Access this Library. EXCEPTION : {file_exp}")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def get_column_elements(self, column_name: str) -> list:
        """
        This method will return the elements from a  particular column in the form of list
        :param column_name: Name of the column to find all its elements
        :return: list of elements in column
        """
        try:
            robot_print_info(f"input path is : {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                if column_name not in self.df.columns:
                    raise Exception(f"Column : {column_name} is not available in given Excel, "
                                    f"Please check again, as it is Case Sensitive ")
                else:
                    elements = self.df[column_name]
                    element_list = elements.to_list()
                    robot_print_info(f"List of elements from column {column_name} is : {element_list}")
                    return element_list
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")

    def get_all_excel_data(self) -> List[dict]:
        """
        This method will return the whole excel in the form of dictionary List
        :return: This method will return the whole excel in the form of dictionary List
        """
        try:
            robot_print_info(f"Input path is : {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                result = self.df.to_dict(orient="records")
                robot_print_info(f"List of Dictionary is : {result}")
                return result
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def get_cell_value(self, unique_key: str, unique_key_column_name: str, get_value_from_column: str) -> str:
        """
        This method will take element from column, find it in given column and will return cell value for the same
        row index and column name 2
        :param unique_key: element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        etc. command to be searched should be in above example format only
        :param unique_key_column_name: name of column in which element is to be searched
        :param get_value_from_column: name of column from which value is to be found
        :return: it will return cell value for respective element and column_name
        """
        try:
            robot_print_info(f"input path is {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                all_elements = self.df[unique_key_column_name].tolist()
                if unique_key_column_name not in self.df.columns or get_value_from_column not in self.df.columns:
                    raise Exception(f"Either of the two columns {unique_key_column_name} and {get_value_from_column}  "
                                    f"or both Columns not in Excel Please check both the Column Names,it should be "
                                    f"Case Sensitive Manner")
                elif unique_key not in all_elements:
                    raise Exception(
                        f"unique_key:{unique_key} not in column:{unique_key_column_name}"
                        f"\n Please check the Element, it should be Case Sensitive Manner")
                else:
                    row = self.df[self.df[unique_key_column_name] == unique_key].index[0]
                    value = self.df.iloc[row, self.df.columns.get_loc(get_value_from_column)]
                    robot_print_info(f"Cell Value for given element and column is : {value}")
                    return value
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def write_to_cell(self, unique_key: str, unique_key_column_name: str, value_to_set: str, write_to_column: str):
        """
        This method takes element and is found in column, along with row index and a new value is set at intersection
        of row index and new column name
        :param unique_key: command to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc.
             command to be searched should be in above example format only
        :param unique_key_column_name: name of the column in which element is to be found
        :param value_to_set: new cell value to be set in the cell
        :param write_to_column: name of column in which cell value is to be set
        """
        try:
            robot_print_info(f"input path is {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                all_elements = self.df[unique_key_column_name].tolist()
                robot_print_info(f"all elements  of column {unique_key_column_name} are : {all_elements}")
                if unique_key_column_name not in self.df.columns or write_to_column not in self.df.columns:
                    raise Exception(f"Either of the two columns {unique_key_column_name} and {write_to_column} "
                                    f"or both Columns not in Excel Please check both the Column Names, it should Case "
                                    f"Sensitive Manner")
                elif unique_key not in all_elements:
                    raise Exception(f"unique_key: {unique_key} is not available in Column : {unique_key_column_name}")
                else:
                    row_index = self.df[self.df[unique_key_column_name] == unique_key].index[0]
                    self.df.at[row_index, write_to_column] = value_to_set
                    robot_print_info(f"dataframe is : {self.df}")
                    self.df.to_excel(self.input_file_path, sheet_name="Command_List", index=False)
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def get_row_by_element(self, unique_key: str, unique_key_column_name: str) -> dict:
        """
        This method will fetch the element in column and will return the data from same row and other columns of Excel
        in the dictionary format
        :param unique_key: command to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP etc.
             command to be searched should be in above example format only
        :param unique_key_column_name: name of the column where element is to be found
        :return: This method will return dictionary of the fetched data
        """
        try:
            robot_print_info(f"input path is {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                robot_print_info(f"file path is : {self.input_file_path}")
                all_elements = self.df[unique_key_column_name].tolist()
                robot_print_info(f"all elements  of column {unique_key_column_name} are : {all_elements}")
                if unique_key_column_name not in self.df.columns:
                    raise Exception(f"Column: {unique_key_column_name} is not available in Excel\n"
                                    f"Please Enter Column Name which is available in Excel,"
                                    f" Column Name should be Case in Sensitive Manner")
                if unique_key not in all_elements:
                    raise Exception(f"unique_key: {unique_key} is not available in Column : {unique_key_column_name}\n"
                                    f"Please Enter Element Name which is available in Column {unique_key_column_name}")
                else:
                    result = self.df[self.df[unique_key_column_name] == unique_key]
                    dictionary = result.to_dict(orient="record")[0]
                    robot_print_info(f"Row elements are : {dictionary}")
                    return dictionary
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def set_column_name(self, existing_column: str, new_column_name: str):
        """
        This method is used to change the name of existing column to a new column name.
        :param existing_column: name of column which is to be changed
        :param new_column_name: New name of the column
        :return:
        """
        try:
            robot_print_info(f"input path is {self.input_file_path}")
            if os.path.exists(self.input_file_path) and os.path.isfile(self.input_file_path):
                robot_print_info(f"file path is : {self.input_file_path}")
                if existing_column not in self.df.columns:
                    raise Exception(f"Column: {existing_column} is not available in Excel\n"
                                    f"Please Enter Column Name which is available in Excel,"
                                    f" Column Name should be Case in Sensitive Manner")
                else:
                    self.df = self.df.rename(columns={existing_column: new_column_name})
                    self.df.to_excel(self.input_file_path, sheet_name="Command_List", index=False)
                    robot_print_info(f"Column Name:{existing_column} changed to {new_column_name}")
            else:
                raise Exception(f"File:{self.input_file_path} does not have required extension : .xlsx "
                                f"or file does not exists OR Directory:{self.parent_folder} does not Exists")
        except Exception as exp:
            robot_print_error(f" EXCEPTION : {exp}")

    def compare_cell_values(self, unique_key: str, unique_key_column_name: str, column_name_1,
                            column_name_2: str) -> bool:
        """
        IT will compare the cell values
        :param unique_key: element to be searched in column, e.g. ALEXA_PLAY_SONG, ALEXA_STOP
        etc. command to be searched should be in above example format only
        :param unique_key_column_name: name of column in which element is to be searched
        :param column_name_1: column_name1 to compare the cell values
        :param column_name_2: column_name2 to compare the cell values
        :return: 
        """
        try:
            all_elements = self.df[unique_key_column_name].tolist()
            if unique_key_column_name not in self.df.columns or column_name_1 not in self.df.columns or column_name_2 not in self.df.columns:
                raise Exception(
                    f"either one of the columns: {unique_key_column_name}, {column_name_1}, {column_name_2} \n"
                    f"is not available in Excel. Please Enter Column Name which is available in Excel,"
                    f" Column Name should be Case in Sensitive Manner")
            if unique_key not in all_elements:
                raise Exception(f"unique_key: {unique_key} is not available in Column : {unique_key_column_name}\n"
                                f"Please Enter Element Name which is available in Column {unique_key_column_name}")
            else:
                column_1_value = self.get_cell_value(unique_key, unique_key_column_name, column_name_1)
                column_2_value = self.get_cell_value(unique_key, unique_key_column_name, column_name_2)
                if column_1_value == column_2_value:
                    robot_print_info(
                        f"cell value : {column_1_value} from column : {column_name_1} and \n"
                        f"cell value : {column_2_value} from column : {column_name_2} are Same")
                    return True
                else:
                    robot_print_info(
                        f"cell value : {column_1_value} from column : {column_name_1} and \n"
                        f"cell value : {column_2_value} from column : {column_name_2} are Not Same")
                    return False
        except Exception as exp:
            robot_print_error(f"EXCEPTION : {exp}")
