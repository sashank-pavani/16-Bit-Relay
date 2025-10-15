import requests
import pandas as pd
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CommonKeywordsClass import CommonKeywordsClass
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.CustomPrint import robot_print_error, robot_print_info
from Robo_FIT.GenericLibraries.GenericOpLibs.TestArtifacts.ProjectConfigManager import ProjectConfigManager


class DataPost:

    def __init__(self):
        self.project_config_file = ProjectConfigManager()
        self.helper = CommonKeywordsClass()
        self.enterproj_id = None
        self.build_number = None

    def convert_excel_to_json(self, excel_file, sheet_name):
        """
        Read the robot xml file
        :return:  the JSON data (data_json) that was obtained by reading and processing the Excel data
        :rtype: returns the data in the form list of the limited packages if packages are empty then returns string
        :raise: FileNotFoundError if Excel file not found
        """
        try:
            package_list = self.project_config_file.get_the_list_of_packages()
            if excel_file is not None and sheet_name is not None:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                if not package_list:
                    robot_print_info(f"The package list is empty hence returning all package values")
                    df.set_index(df.columns[1], inplace=True)
                    df = df.iloc[:, 1:]
                    data_json = df.to_json(orient="index", date_format="iso")
                    return data_json
                for column_name in package_list:
                    if column_name not in df.columns:
                        raise ValueError(f"Column '{column_name}' not found in the Excel sheet")
                output_list = []
                for row in df.itertuples(index=False):
                    json_row = {'Time(milliseconds)': f"{row[0]}", 'Iteration': int(f"{row[1]}")}
                    for col in package_list:
                        value = row[df.columns.get_loc(col)]
                        try:
                            precision = len(str(value).split('.')[1])
                            json_row[col] = round(float(value), precision)
                        except ValueError:
                            json_row[col] = f"{value}"
                    output_list.append(json_row)
                return output_list
        except Exception as exp:
            robot_print_error(f"Error to convert excel data to json format , EXCEPTION: {exp}")

    def build_data(self):
        """
        Get enterproj ID for porject and Build number
        """
        self.enterproj_id = self.project_config_file.get_project_enterproj_id()
        self.build_number = self.helper.build_number

    def post_data(self, url, data_json):
        """
        Post data and json_data to API endpoint given specific URL
        :return:  the JSON data (data_json) that was obtained by reading and processing the Excel data
        """
        try:
            self.build_data()
            data = {'project_ID': self.enterproj_id, 'build_number': self.build_number}
            response = requests.post(url, files={'file': data_json}, data=data)
            if response.status_code == 200:
                robot_print_info("Data successfully posted to the API.")
            else:
                robot_print_error(f"Failed to post data. Status code: {response.status_code}. Error: {response.text}")
        except Exception as exp:
            robot_print_error(f"Failed to post data , EXCEPTION: {exp}")