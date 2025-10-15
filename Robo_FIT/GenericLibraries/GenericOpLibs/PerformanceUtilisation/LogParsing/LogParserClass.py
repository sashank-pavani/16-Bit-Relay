import re


class LogParserClass:
    """
    This class is used for create the dataset for particular format
    """
    def __init__(self, i_search_pattern, i_data_seperator, i_data_index, i_column_name, i_increase_row=False,i_is_dynamic=False):
        """
        This init is used for create the dataset with the help of given args
        :param i_search_pattern : Regular expression of the string which you want to match
        :param i_data_seperator : seperator is how data you want to separate from finding in file
        :param i_data_index : Which Index value of key you want to insert on excel or df
        :param i_column_name : column name for values
        :param i_increase_row : True if you want to increase row by the column (for eg, time)
        :param i_is_dynamic : this for package and value mapping (refer showmem -a)
        """
        self.SEARCH_PATTERN = i_search_pattern
        self.DATA_SEPERATOR = i_data_seperator
        self.DATA_INDEX = i_data_index
        self.COL_NAME = i_column_name
        self.INCREASE_ROW = i_increase_row
        self.search_re = re.compile(self.SEARCH_PATTERN)
        self.IS_DYNAMIC = i_is_dynamic
